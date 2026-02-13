import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def load_yaml(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def generate_nodes(context):
    config_file_name = LaunchConfiguration("config_file").perform(context)
    config_file_pkg = FindPackageShare(LaunchConfiguration("config_pkg")).perform(context)
    configs = load_yaml(os.path.join(config_file_pkg, "config", config_file_name))
    nodes = []
    for item_name, config in configs.items():
        nodes.append(
            Node(
                package="spacemouse_ros2",
                executable="pyspacemouse_publisher",
                name="spacemouse_publisher",
                namespace=str(config["namespace"]),
                output="screen",
                parameters=[
                    {"operator_position_front": config["operator_position_front"]},
                    {"device_path": str(config["device_path"])},
                ],
            )
        )
    return nodes

def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value="example_config.yaml",
                description="Name of the spacemouse configuration file to load",
            ),
            DeclareLaunchArgument(
                "config_pkg",
                default_value="spacemouse_ros2",
                description="Name of the package containing the spacemouse configuration file",
            ),
            OpaqueFunction(function=generate_nodes),
        ]
    )
