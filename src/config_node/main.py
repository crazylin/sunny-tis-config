from datetime import datetime
import json
import zmq
import time
from threading import Thread
import rclpy
from ros_node import RosNode, from_parameter_value
from threading import Lock
from zmq.utils import jsonapi
import numpy as np
from point_data import SeamData

params ={
            'camera_tis_node': {'exposure_time': 1000, 'power': False},
            'gpio_raspberry_node': {'laser': False},
            'seam_tracking_node': {
                'codes': [],
                'task': -1,
                'delta_x': 0.,
                'delta_y': 0.,
                'enable': False,
                'window_size': 10,
                'gap': 2,
                'step': 2.,
                'length': 5},
            'laser_line_center_node': {
                'ksize': 5,
                'threshold': 35,
                'width_min': 1.,
                'width_max': 30.},
            'laser_line_filter_node': {
                'enable': False,
                'window_size': 10,
                'gap': 5,
                'deviate': 5.,
                'step': 2.,
                'length': 30},
            'line_center_reconstruction_node': {
                'homography_matrix': [
                    0.16085207487679626, 0.2679666549425936, -205.1548588898662,
                    -0.7409214060537485, 0.009161773590904738, 758.7035197990384,
                    0.0060885745075360325, 4.084389881288615e-06, 1.0]
            }
        }

       
# params_cb = {
#             'camera_tis_node': {'power': params_cb_power},
#             'gpio_raspberry_node': {'laser': params_cb_laser},
#             'seam_tracking_node': {'task': params_cb_task},
#             'line_center_reconstruction_node': {'homography_matrix': params_cb_homography}
#         }

dtype = [(x, np.float32) for x in 'xyi']


pub_socket:zmq.Socket
rep_socket:zmq.Socket
thExist:bool = False
ros:RosNode
seam_data = SeamData()


# def params_cb_power( b: bool):
#     pub_socket.send_multipart([b"Power",str(b)])
# def params_cb_laser( b: bool):
#     pub_socket.send_multipart([b"Laser",str(b)])
# def params_cb_task( task: int):
#     pub_socket.send_multipart([b"Task",str(task)])
# def params_cb_homography(h):
#     pub_socket.send_multipart([b"Homography",jsonapi.dumps(h)])


def ros_cb_seam(msg):
    try:
        seam_data.from_msg(msg)
        d, id, fps = seam_data.get()
        if int(id) % 2 == 0:
            return
        new_msg = {"id":id,"fps":fps,"i":np.array(d["i"]).tolist(),"x":np.array(d["x"]).tolist(),"y":np.array(d["y"]).tolist()}
        pub_socket.send_multipart([b"Seam",jsonapi.dumps(new_msg)])
    except Exception as e :
        return

# def ros_cb_pnts(msg):
#     pub_socket.send_multipart([b"Pnts",jsonapi.dumps(msg)])
def ros_cb_log(msg):
    try:
        new_msg = {"level":  msg.level, "name": msg.name, "msg": msg.msg}
        pub_socket.send_multipart([b"Log",jsonapi.dumps(new_msg)])
    except Exception as e :
        return

def rep_server(socket):
    while thExist:
        try :
            command,name,data = rep_socket.recv_multipart()
            command = command.decode("UTF-8")
            name = name.decode("UTF-8")
            data = data.decode("UTF-8")
            if command == "get_params" :
                reqNames = json.loads(data)
                future = ros.get_params(name, reqNames)
                dic = dict()
                if future != None:
                    count = 0
                    for p in future.values:
                        dic[reqNames[count]] = from_parameter_value(p)
                        count+=1
                rep_socket.send_multipart([b"get_params",json.dumps(dic).encode("utf8")])
            elif command == "set_params" :
                future = ros.set_params(name, json.loads(data))
                ret = []
                for result in future.results:
                    ret.append({"successful":result.successful,"reason":result.reason})
                rep_socket.send_multipart([b"set_params",json.dumps(ret).encode("utf8")])
            elif command == "pub_config" :
                ret = ros.pub_config(data)
                rep_socket.send_multipart([b"pub_config",json.dumps(ret).encode("utf8")])
        except Exception as e :
            continue
 
if __name__ == '__main__':
    rclpy.init()

    ros = RosNode(params)
    ros.sub_seam(ros_cb_seam)
    ros.sub_log(ros_cb_log)
    #ros.sub_pnts(ros_cb_pnts)
    ros_thread = Thread(target=rclpy.spin, args=[ros])
    ros_thread.start()

 

    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5566")

    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5577")

    thExist = True
    rep_socket_thread = Thread(target=rep_server, args=[rep_socket])
    rep_socket_thread.start()

    ros_thread.join()
    ros.destroy_node()

    thExist = False
    rep_socket_thread.join()
    rclpy.shutdown()

    