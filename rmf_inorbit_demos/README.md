# Full Control InOrbit/RMF Fleet Adapter Demos

![InOrbit + Open-RMF](assets/open%20rmf%20inorbit%20github%20header%20narrow%202.png)

This package provides a configuration of the [Full Control InOrbit/RMF Fleet Adapter](https://github.com/inorbit-ai/ros_amr_interop/tree/humble-devel/rmf_inorbit_fleet_adapter) which is ready to be used with an already-configured [InOrbit](https://www.inorbit.ai/product) demo account provided by the InOrbit team. It will help you understand how [Open-RMF](https://github.com/open-rmf/rmf#robotics-middleware-framework-rmf) and InOrbit work together without the need to set-up simulations or real robots.

## Overview

This guide will take you through the process of setting up your local machine to run RMF and the InOrbit Fleet Adapter in the demonstration environments, and will explain how the Fleet Adapter works. These demos run on a simulated warehouse with multiple robots inside it that can be monitored via InOrbit.

![mission video](assets/full%20mission.gif)

## Account setup

This demo is set-up to use a specific InOrbit location with three robots. A demo account with this set-up already prepared is available upon request, and will give you access to a three robot simulation and some of the most important features of the InOrbit Platform for the full experience.

To request access to the InOrbit demo account, please send an email to [`success@inorbit.ai`](success@inorbit.ai). You will be granted temporary access to the InOrbit Control UI and a matching API Key to use with the fleet adapter. This user and API Key will have access to a location with three robots in a pre-created InOrbit Enterprise Edition account.

In order to use your own InOrbit account with your own robot fleet, check the [template package](https://github.com/inorbit-ai/rmf_inorbit_examples/tree/main/rmf_inorbit_template).

## Environment setup

Both RMF and the fleet adapter run on a machine separated from the robots. You will need access to an Ubuntu 22.04 box or use our Docker setup to get the fleet adapter running. To achieve this, first follow the instructions in the fleet adapter package [guide](https://github.com/inorbit-ai/ros_amr_interop/tree/humble-devel/rmf_inorbit_fleet_adapter/rmf_inorbit_fleet_adapter#setup) and once the fleet adapter is built and the dependencies installed, follow the next steps:

- Clone the examples repository inside the src folder of your workspace:

```
cd ~/ws/src
git clone https://github.com/inorbit-ai/rmf_inorbit_examples
```

- Add the API key you obtained from InOrbit as an environment variable:

```
echo "export INORBIT_API_KEY=<your api key>" >> ~/.bashrc
source ~/.bashrc
# If in a docker environment, remember to commit the changes at the exit trap when exiting the container
```

- Build the package:

```
cd ~/ws
colcon build
```

## Start a demo

Open the invitation link you received to your email in a Chrome browser. The URL should have the form `https://control.inorbit.ai/join?inviteCode=xxxxx` After completing the tutorial, go to the the `Navigation` dashboard and in the text box at the top bar, type `Tugz335` and press Enter.

![navigation dashboard annotated](assets/navigation%20dashboard%20annotated.png)

NOTE: What your are seeing is not a real warehouse, but an overlap of three different simulations with one robot each based on [aws-robomaker-small-warehouse-world](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world). Even though the robots cannot collide with each other, RMF will receive their data as if they were in the same place and will orchestrate all of the movements accordingly.

**Important note:** If the robots don't move as expected after starting the demo or if the robots are already moving, the lock might be on (see the above picture and locate the indicator, which in this example shows unlocked). If the robots are locked, **do not break the lock!** Someone else might be playing with the same robots, and two active controllers at the same time will cause problems.

InOrbit Control provides a lot of useful information. For this particular application, the `Fleet` dashboard might be of your interest, but feel free to explore all of them!

The `rmf_inorbit_demos` package contains two important folders:

- `config/`: It includes the configurations files that the adapter needs to be able to connect to the fleet. Each of the subdirectories has the set of files corresponding to a certain demo. These files are:
  - `adapter.config.yaml`: Contains all of the information about the fleet in general and about each specific robot.
  - `<demo name>.building.yaml`: Building description file, as generated by [`traffic-editor`](https://osrf.github.io/ros2multirobotbook/traffic-editor.html). It can be opened by `traffic-editor` to visualize and edit the navigation graph.
  - `nav_graph.yaml`: Is the navigation graph that contains information about each lane, like its allowed directions, and about each vertex, like whether it is a charging spot or a don't-park spot. It is the output of running [`building_map_generator nav`](https://osrf.github.io/ros2multirobotbook/simulation.html#building-map-generator) over the `.building.yaml` file of `traffic-editor`.
  - Two PNG images are also included: The map image downloaded from InOrbit, and an screenshot of `traffic-editor` showing the navigation graph.
- `launch/`: It contains the necessary launch files to launch the adapter with specific the settings of a certain demo, as well as all of the core components of `Open-RMF`

In order to run a demo, you have to launch the desired launch file, named `<demo name>.launch.xml`. For example:

```
ros2 launch rmf_inorbit_demos warehouse.launch.xml
```

Doing so will launch `RMF` and the fleet adapter, logging all messages to the console. The robots will move the positions designated in the `robots` section of the `adapter.config.yaml` file.

## Send a task

A user can request a robot do something by using RMF [tasks](https://osrf.github.io/ros2multirobotbook/task.html#tasks-in-rmf). The way this works is the following:

- A task is submitted
- RMF analyzes the situation surrounding each robot in a fleet, each fleet, and the capabilities of each fleet to decide through a bidding process to which robot the task should be assigned, optimizing the process to the shortest duration possible.
- The robot assigned will try to accomplish the task. After that, it will move to either a safe spot or a charger (depending on the fleet configuration in `adapter.config.yaml`) and remain idle until a new task is assigned to it.

![Bid for tasks explanatory chart](https://osrf.github.io/ros2multirobotbook/images/rmf_core/rmf_bidding.png)
Image courtesy of [OSRF](https://www.openrobotics.org/), extracted from [here](https://osrf.github.io/ros2multirobotbook/task.html).

Our demos currently support only [Loop](https://osrf.github.io/ros2multirobotbook/task_types.html?highlight=loop#loop-task) actions, which request RMF to send a robot to patrol for a certain number of times between to named vertices in the graph. You can see the name of the vertices in the `nav_graph.yaml` file of the demo or by looking at the provided screenshot of `traffic-editor`.

To submit a Loop task, you can use the tool included in the package:

```
# Use -h to show help
example@container:~/ws$ ros2 run rmf_inorbit_demos dispatch_loop -h
usage: dispatch_loop [-h] -s START -f FINISH [-n LOOP_NUM]
                     [-st START_TIME] [-pt PRIORITY]
                     [--use_sim_time]

options:
  -h, --help            show this help message and exit
  -s START, --start START
                        Start waypoint
  -f FINISH, --finish FINISH
                        Finish waypoint
  -n LOOP_NUM, --loop_num LOOP_NUM
                        Number of loops to perform, default: 1
  -st START_TIME, --start_time START_TIME
                        Start time from now in secs, default: 0
  -pt PRIORITY, --priority PRIORITY
                        Priority value for this request, default:
                        0
  --use_sim_time        Use sim time, default: false
```

To send a robot to loop between vertices named `dock1` and `p03` 2 times, run:

```
ros2 run rmf_inorbit_demos dispatch_loop -s dock1 -f p03 -n 2
```

You can see the location of these vertices in the provided screenshot of traffic editor. Try to guess which robot will be chosen and which path it will take.

![robot navigating with path and graph](assets/robot%20navigating%20with%20path%20and%20graph.png)

## Modifying the demos

You can play around with the settings in `adapter.config.yaml` or edit the building description graph in `traffic-editor` and export a new navigation graph. The possible settings and the setup process is explained in our [template package](https://github.com/inorbit-ai/rmf_inorbit_examples/tree/main/rmf_inorbit_template).

## Troubleshooting

If no robots move, they might be locked by another adapter. Check the lock icon in the top bar for each of the robots and if they are locked, wait for the lock to expire or to be opened before running your demo.

If some robots are not moving, check their battery level by clicking their avatar in the map and looking at their vitals. If their battery level drained below the threshold specified in the `adapter.config.yaml` file of the demo (usually 20%), the robot will not move. Battery drains happen when the robots are not docked after RMF is shut down. You can send a robot to dock or hot-swap its batteries using the `actions` menu in the top bar of the navigation dashboard.

All log messages are logged to the console. If you are having trouble, look for warnings or errors. You can use [`rqt_console`](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Using-Rqt-Console/Using-Rqt-Console.html), which is included in our docker image.

If you inspect the ROS2 environment you will see the following the features listed below were launched. Most are part of `RMF` functionality. To see exactly which are being launched by our fleet adapter, see [here](https://github.com/inorbit-ai/ros_amr_interop/tree/humble-devel/rmf_inorbit_fleet_adapter/rmf_inorbit_fleet_adapter#nodes). If you see certain nodes are missing, the system might be malfunctioning.

Feel free to contact the InOrbit team at `support@inorbit.ai` for further questions.

### Nodes

```
/{fleet name}_fleet_adapter
/inorbit_fleet_command_handle

/door_supervisor
/rmf_dispatcher_node
/rmf_lift_supervisor
/rmf_traffic_blockade_node
/rmf_traffic_schedule_primary
```

### Topics

```
/adapter_door_requests
/adapter_lift_requests
/dispatch_states
/dispenser_requests
/dispenser_results
/dispenser_states
/dock_summary
/door_requests
/door_states
/door_supervisor_heartbeat
/fire_alarm_trigger
/fleet_states
/ingestor_requests
/ingestor_results
/ingestor_states
/lane_states
/lift_requests
/lift_states
/nav_graphs
/rmf_task/bid_notice
/rmf_task/bid_response
/rmf_task/dispatch_ack
/rmf_task/dispatch_request
/rmf_traffic/blockade_cancel
/rmf_traffic/blockade_heartbeat
/rmf_traffic/blockade_reached
/rmf_traffic/blockade_ready
/rmf_traffic/blockade_release
/rmf_traffic/blockade_set
/rmf_traffic/heartbeat
/rmf_traffic/itinerary_clear
/rmf_traffic/itinerary_delay
/rmf_traffic/itinerary_extend
/rmf_traffic/itinerary_reached
/rmf_traffic/itinerary_set
/rmf_traffic/negotiation_ack
/rmf_traffic/negotiation_conclusion
/rmf_traffic/negotiation_forfeit
/rmf_traffic/negotiation_notice
/rmf_traffic/negotiation_proposal
/rmf_traffic/negotiation_refusal
/rmf_traffic/negotiation_rejection
/rmf_traffic/negotiation_repeat
/rmf_traffic/negotiation_states
/rmf_traffic/negotiation_statuses
/rmf_traffic/participants
/rmf_traffic/query_update_1
/rmf_traffic/registered_queries
/rmf_traffic/schedule_inconsistency
/rmf_traffic/schedule_startup
/task_api_requests
/task_api_responses
/task_summaries
```

### Services

```
/<InOrbitSite>_fleet_adapter/describe_parameters
/<InOrbitSite>_fleet_adapter/get_parameter_types
/<InOrbitSite>_fleet_adapter/get_parameters
/<InOrbitSite>_fleet_adapter/list_parameters
/<InOrbitSite>_fleet_adapter/set_parameters
/<InOrbitSite>_fleet_adapter/set_parameters_atomically
/cancel_task
/door_supervisor/describe_parameters
/door_supervisor/get_parameter_types
/door_supervisor/get_parameters
/door_supervisor/list_parameters
/door_supervisor/set_parameters
/door_supervisor/set_parameters_atomically
/get_dispatches
/inorbit_fleet_command_handle/describe_parameters
/inorbit_fleet_command_handle/get_parameter_types
/inorbit_fleet_command_handle/get_parameters
/inorbit_fleet_command_handle/list_parameters
/inorbit_fleet_command_handle/set_parameters
/inorbit_fleet_command_handle/set_parameters_atomically
/rmf_dispatcher_node/describe_parameters
/rmf_dispatcher_node/get_parameter_types
/rmf_dispatcher_node/get_parameters
/rmf_dispatcher_node/list_parameters
/rmf_dispatcher_node/set_parameters
/rmf_dispatcher_node/set_parameters_atomically
/rmf_lift_supervisor/describe_parameters
/rmf_lift_supervisor/get_parameter_types
/rmf_lift_supervisor/get_parameters
/rmf_lift_supervisor/list_parameters
/rmf_lift_supervisor/set_parameters
/rmf_lift_supervisor/set_parameters_atomically
/rmf_traffic/register_participant
/rmf_traffic/register_query
/rmf_traffic/request_changes
/rmf_traffic/unregister_participant
/rmf_traffic_blockade_node/describe_parameters
/rmf_traffic_blockade_node/get_parameter_types
/rmf_traffic_blockade_node/get_parameters
/rmf_traffic_blockade_node/list_parameters
/rmf_traffic_blockade_node/set_parameters
/rmf_traffic_blockade_node/set_parameters_atomically
/rmf_traffic_schedule_primary/describe_parameters
/rmf_traffic_schedule_primary/get_parameter_types
/rmf_traffic_schedule_primary/get_parameters
/rmf_traffic_schedule_primary/list_parameters
/rmf_traffic_schedule_primary/set_parameters
/rmf_traffic_schedule_primary/set_parameters_atomically
/submit_task
```

![Powered by InOrbit](assets/open%20rmf%20inorbit%20github%20footer.png)
