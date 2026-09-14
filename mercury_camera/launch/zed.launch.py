from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, Shutdown, OpaqueFunction
from launch_ros.actions import PushRosNamespace, ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression, LaunchConfiguration as LC
from ament_index_python import get_package_share_directory
import os

def launch_picture_taker(context, *args, **kwargs):
    launch_items = []

    if LC("picture_taker_enabled").perform(context) != "True":
        return launch_items
    
    launch_items.append(
        Node(
            package='mercury_camera',
            executable='picture_taker.py',
            name='picture_taker',
            output='screen',
            parameters=[
                {"robot_namespace": LC("robot")},
                {"camera_name": "ffc"},
                {"subscription_enabled": True},
                {"save_stereo": False},
                {"save_split": True}
            ]
        )
    )

def generate_launch_description():

    # Define common configuration path
    zed_config_path = os.path.join(
        get_package_share_directory('zed_wrapper'),
        "config",
        "common_stereo.yaml"
    )

    # Paths for individual camera configurations

    # Zed X Mini
    zedxm_camera_path = os.path.join(
        get_package_share_directory('zed_wrapper'),
        'config',
        'zedxm.yaml'
    )

    # FFC Overrides
    ffc_config_path = os.path.join(
        get_package_share_directory('mercury_camera'),
        'config',
        'ffc_config.yaml'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name="robot",
            default_value="mercury",
            description="name of the robot"
        ),
        DeclareLaunchArgument(
            "picture_taker_enabled",
            default_value="False",
            description="Enable picture taker for camera calibration"
        ),
        # Group actions under the robot namespace
        GroupAction([
            PushRosNamespace(LC("robot")),

            ComposableNodeContainer(
                name="ffc_container",
                namespace="",
                package="rclcpp_components",
                executable="component_container",
                output="screen",
                respawn=True,
                composable_node_descriptions=[
                    # First ZED Node (FFC)
                    ComposableNode(
                        package="zed_components",
                        plugin="stereolabs::ZedCamera",
                        namespace="ffc",
                        name="zed_node",
                        parameters=[
                            zed_config_path,
                            zedxm_camera_path,
                            ffc_config_path
                        ]
                    ),
                ],
            ),
            # Used for taking pictures, good for camera calibration
            OpaqueFunction(function=launch_picture_taker)
            
        ], scoped=True),


    ])
