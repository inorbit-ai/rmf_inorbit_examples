# rmf_inorbit_template

![InOrbit + Open-RMF](assets/open%20rmf%20inorbit%20github%20header%20narrow%202.png)

This is a template package for the configuration of the [InOrbit Fleet Adapter](https://github.com/inorbit-ai/ros_amr_interop/tree/humble-devel/rmf_inorbit_fleet_adapter), where the configuration files are stored and forwarded to the fleet adapter.
This setup guide assumes you are an InOrbit customer with an existing fleet of robots (it can be a fleet of one) in a real location, already configured within the InOrbit platform. If you are not a customer yet or you don't have access to a fleet, go to [rmf_demos](https://github.com/inorbit-ai/rmf_inorbit_examples/tree/main/rmf_inorbit_demos) to see the adapter in action in one of the InOrbit simulated environments. We also recommend reading the [documentation](https://github.com/inorbit-ai/rmf_inorbit_examples/tree/main/rmf_inorbit_demos/README.md) of the demos to understand how the fleet adapter works, and then follow the instructions below to configure your fleets to work with RMF.

## Get the InOrbit RMF Fleet Adapter

Go to [ros_amr_interop/rmf_inorbit_fleet_adapter](https://github.com/inorbit-ai/ros_amr_interop/tree/humble-devel/rmf_inorbit_fleet_adapter) and follow the instructions to get the fleet adapter working on your machine.

## Configure your InOrbit account

1. Get an active InOrbit account for your organization. Log into InOrbit at [https://console.inorbit.ai/](console.inorbit.ai).
2. Go to the [configuration](https://console.inorbit.ai/configuration) page and navigate to the API key tab.
3. Click in the **+** sign and create an API key. In the `role` dropdown menu, select **Operator**.
4. Show the API key by clicking in the eye icon and the copy it.

![api key tab](assets/api%20key.png)

- In your local workspace, you can choose to set this API key as an environment variable under the name of INORBIT_API_KEY or pass it to the adapter explicitly on launch. To set it permanently as an environment variable:

```
# From inside the container:
echo  “INORBIT_API_KEY=<your api key>” >> ~/.bashrc
source ~/.bashrc

# If in a docker environment, remember to commit the changes at the exit trap when exiting the container
```

## Configure RMF and the InOrbit Fleet Adapter

- Get the map metadata of the fleet location using the [InOrbit REST API](https://api.inorbit.ai/docs/index.html). Tip: you can download [our Postman collection](https://api.inorbit.ai/docs/index.html#tag/Postman). Use [this endpoint](https://api.inorbit.ai/docs/index.html#operation/getCurrentMap) with the `robotId` of one of the robots of your fleet that is currently operating in the location the adapter will be used, authorizing with the previously created API key. This is an example response body:

```json
{
  "robotId": "376796497",
  "mapId": "map",
  "updatedTs": 1676557293261,
  "label": "map",
  "dataHash": "2475836613394213593",
  "height": 719,
  "width": 1066,
  "resolution": 0.019999999552965164,
  "x": -10.609999656677246,
  "y": -7.175000190734863
}
```

- Head over to `my_adapter.config.yaml` in the `config` folder and scroll down to the `MAP CONFIG` section. Copy the `x` and `y` values from the map metadata into the config file. For this example, it should look like this:

```yaml
# MAP CONFIG ===================================================================
# The values are used to compute the transformations between InOrbit and RMF coordinate systems
# Copy the X and Y values from the map metadata downloaded from InOrbit

map:
  # Please, don't forget to update the values
  x: -10.609999656677246
  y: -7.175000190734863
```

- Use [this endpoint](https://api.inorbit.ai/docs/index.html#operation/downloadMap) with the same `robotId` used in the first step and the `mapId` extracted from the metadata requested. Save the image in the `config` directory of the template.
- The downloaded image will look flipped compared to the actual place. Flip the image back using a [command line tool](https://imagemagick.org/script/command-line-options.php#flip) or [graphical image editor](https://www.gimp.org/). For details on why this happens, see [here](https://developer.inorbit.ai/docs#maps).
- Calculate the width and height of the map in meters by multiplying the resolution value of the map by the size in pixels of the image. For the example map metadata shown above, these numbers are:
  - HeightMeters = HeightPx \* resolution = 719px \* 0.02m/px = 14.38m
  - WidthMeters = WidthPx \* resolution = 1066px \* 0.02m/px = 21.32m
- From inside the container, launch `traffic-editor` and create the building description file with the help of the [tutorial](https://osrf.github.io/ros2multirobotbook/traffic-editor.html) in the Open-RMF book and:
  - Use the map image downloaded in the previous step.
  - Using the calculated length or width of the map, whichever is greater, add a measurement of one side of the map to scale it. Note that setting the scale using the textbox in the side panel has no effect. Save the map and restart traffic-editor afterwards.
  - Create as many one way or two way traffic lanes as you need. For more information, checkout the [minimum map information required](https://osrf.github.io/ros2multirobotbook/integration_nav-maps.html?highlight=parking#minimum-map-information-required).
  - Make sure you add names and attributes to relevant vertices. You may want to set some vertices as passthrough points, to prevent robots from waiting in those points, or as parking/charger spots on which the robots can idle safely.
  - For charging docks, make sure the vertex is as close to the real location of the dock as possible, and give each charger a relevant `dock_name` and set `is_charger` to `true`.
- Example map created in the Traffic Editor:

![traffic-editor annotated screenshot](assets/traffic-editor%20annotated%20screenshot.png)

- Save the file inside the configuration folder with a meaningful name, like `<building name>.building.yaml`
- Generate the navigation graph using the `building_map_generator` tool from Open-RMF and the file created in the previous step by running `ros2 run rmf_building_map_tools building_map_generator nav <path to the file> <package config directory>` as described in the last part of [this section](https://osrf.github.io/ros2multirobotbook/simulation.html#building-map-generator). Change the name of the file to `nav_graph.yaml`.
- Go to the `robots` section in `my_adapter.config.yaml` and add all of the robots in your fleet using their `robot_id`s.
- For each of the robots on the fleet, [request their attribute definitions](https://api.inorbit.ai/docs/index.html#operation/getRobotAttributeDefinitions). Find the data sources for the battery charge level and the battery charging add them to the robot configuration. If you haven't defined such attributes yet, take a look at [this guide](https://www.inorbit.ai/docs#customize-robot).
- To configure docking, for each robot follow the next steps:
  - [Configure](https://developer.inorbit.ai/docs#configuring-action-definitions) an [action](https://www.inorbit.ai/docs#configure-actions) for docking at one of the chargers you set in the traffic editor.
  - Go to the `robots` section in `my_adapter.config.yaml` and in the `actions` section configure `dock` with the `action_id` of the just created action and the `dock_name` set in traffic editor of the charger vertex.
- For example, for a fleet of two robots, with docking enabled, the `robots` section of the configuration should look like this:

```yaml
robots:
  SirCleansalot:
    robot_config:
      max_delay: 10.0
      # InOrbit specific config
      robot_id: "123456"
      battery_attribute_id: "9CNkeDMTFEAsl"
      charging_status_attribute_id: "GeCbVvUI7NgDv1f_"
      actions:
        dock:
          action_id: "PublishToTopic-0pxSHM"
          dock_name: "charger-vertex-name"
    rmf_config:
      robot_state_update_frequency: 0.5
      start:
        map_name: "my_warehouse"
        waypoint: "start-vertex-name"
        orientation: 0.0
      charger:
        waypoint: "charger-vertex-name"
  Jarvis:
    robot_config:
      max_delay: 10.0
      robot_id: "654321"
      battery_attribute_id: "8CNkeDMTFEAfl"
      charging_status_attribute_id: "GeCbVvUI98gDv1f_"
      actions:
        dock:
          action_id: "PublishToTopic-AslHf"
          dock_name: "charger-vertex-name"
    rmf_config:
      robot_state_update_frequency: 0.5
      start:
        map_name: "my_warehouse"
        waypoint: "start-vertex-name"
        orientation: 0.0
      charger:
        waypoint: "charger-vertex-name"
```

## Launch files

Two launch files are provided:

- `common.launch.xml`: Takes the configuration files and RMF specific parameters with default values and launches all commonly launched RMF modules that are needed for a basic setup, plus the fleet adapter from `rmf_inorbit_fleet_adapter`.
- `template.launch.xml`: Calls the `common.launch.xml` file passing it the configuration files. Adjust the file names to your custom package.

## Rename the package

You may want to rename your custom configuration package. For that, edit the folder name and the `package.xml` and `CMakeLists.txt` files to reflect the changes. The references to this package in the launch files, like the path in the include tag for the `common.launch.xml` file, for example, must be updated too.

## Run the adapter

After making changes to the configuration, the package has to be rebuilt for the changes to take effect. For that, run `colcon build`.

Every time a new shell is opened, the overlay must be sourced. To that, run `. install/local_setup.bash` at `~/ws`.

To launch your custom launchfile, use `ros2 launch <custom_pkg_name> <custom_launchfile_name> <parameters>`. If you kept the original naming and parameters, it would be `ros2 launch rmf_inorbit_template template.launch.xml`.

The robots will navigate to their respective starting vertices.
To see what nodes, topics and services should be running, inspect your ROS environment and compare it to what is listed in [rmf_inorbit_demos documentation](https://github.com/inorbit-ai/rmf_inorbit_examples/tree/main/rmf_inorbit_demos/README.md#nodes).

## Send a task

The `rmf_inorbit_demos` package includes a tool that can be used to generate and send loop tasks to RMF. You can send as many different tasks as you want and RMF will assign the tasks to the most appropriate fleet and robot in the fleet.
To get some help on what it does, run:

```
ros2 run rmf_inorbit_demos dispatch_loop -h
```

To send a task that loops twice from the vertex named `dock` to the vertex `e03`, for example, run the following:

```
ros2 run rmf_inorbit_demos dispatch_loop -s dock -f e03 -n 2
```

![Powered by InOrbit](assets/open%20rmf%20inorbit%20github%20footer.png)
