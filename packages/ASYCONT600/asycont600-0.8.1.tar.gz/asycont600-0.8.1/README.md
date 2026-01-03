# ASYCONT600 Axis Control Unit Instrument Interface
- [ASYCONT600 Axis Control Unit Instrument Interface](#asycont600-axis-control-unit-instrument-interface)
  - [Microservice configuration](#microservice-configuration)
  - [Requirements](#requirements)
    - [Runtime](#runtime)
    - [Development](#development)
  - [Endpoints](#endpoints)

This microservice covers XML based directives which are sent by TCP connection.   
Instrument manual can be found in **doc** folder. 

## Microservice configuration

- HTTP server
- Listening port is **7339** (Can bu configured)
- Listens from all network IPs
- Developed with ASP.NET Core with .NET 8.0

## Requirements

### Runtime

- .NET 8.0 Runtime

``` powershell
winget install Microsoft.DotNet.Runtime.8  # Windows only
```

- ASP.NET Core 8.0 Runtime

``` powershell
winget install Microsoft.DotNet.AspNetCore.8  # Windows only
```

### Development

- .NET 8.0 SDK

``` powershell
winget install Microsoft.DotNet.SDK.8  # Windows only
```



## Endpoints

| Method | Path                                | Definition                                             |
| ------ | ----------------------------------- | ------------------------------------------------------ |
| PUT    | /move/{move_type}/{axis}/{position} | Move axis to desired position                          |
| PUT    | /reference/{axis}/{position}        | Set current position as the desired reference for axis |
| PUT    | /home/{axis}                        | Starts preset homing procedure for the axis            |
| PUT    | /quickstop/{axis}                   | Immediately stop axis                                  |
| PUT    | /quickstop                          | Immediately stop all axes                              |
| PUT    | /bringxy                            | Bring X and Y axis to probe mounting position          |

Where the endpoint parameters are:

| Parameter   | Options                      |
| ----------- | ---------------------------- |
| {move_type} | absolute, relative           |
| {axis}      | x, y, z, pol, slide, azimuth |
| {position}  | [user input]                 |

<u>Note</u>: **bringxy** command moves x axis to lower limit and y axis to lower limit plus 0.5 meters.  
