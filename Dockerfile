
FROM ros:galactic AS deploy

RUN echo "source /opt/ros/galactic/setup.bash" >> /root/.bashrc

RUN groupadd --gid 1000 ros \
  && useradd -s /bin/bash --uid 1000 --gid 1000 -m ros \
  && usermod -a -G video ros \
  && echo "source /opt/ros/galactic/setup.bash" >> /home/ros/.bashrc

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pyzmq

COPY ./config_node/ros2_numpy /usr/lib/python3/dist-packages/ros2_numpy

# CMD [ "python3", "/workspace/sunny-tis-config/src/config_node/main.py" ]

# Run colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

#RUN mkdir -p src && cd src && git clone https://github.com/ros/ros_tutorials.git -b galactic-devel

#RUN rosdep update && rosdep install -i --from-path src --rosdistro galactic -y

# RUN apt-get update && apt-get install --no-install-recommends -y \
#     build-essential \
#     git \
#     python3-colcon-common-extensions \
#     python3-colcon-mixin \
#     python3-rosdep \
#     python3-vcstool \
#     wget \
#     nano \
#     && rm -rf /var/lib/apt/lists/*



# RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
#     && dpkg -i packages-microsoft-prod.deb \
#     && rm packages-microsoft-prod.deb \
#     && apt-get update \
#     && apt-get install -y apt-transport-https \
#     && apt-get install -y dotnet-sdk-3.1



# RUN apt-get install -y ros-galactic-test-msgs \
#     && apt-get install -y ros-galactic-fastrtps ros-galactic-rmw-fastrtps-cpp \
#     && apt-get install -y ros-galactic-cyclonedds ros-galactic-rmw-cyclonedds-cpp

# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends git
#WORKDIR '/workspace'

#RUN git clone https://github.com/RobotecAI/ros2cs.git

#RUN cd ros2cs && ./get_repos.sh

#RUN cd ros2cs && . /opt/ros/galactic/setup.sh && ./build.sh

#RUN cd ros2cs && . /opt/ros/galactic/setup.sh && . /opt/ros/galactic/local_setup.sh && ./build.sh