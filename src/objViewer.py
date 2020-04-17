import os
import open3d as o3d


def render(obj_file):
    mesh = o3d.io.read_triangle_mesh(obj_file)
    o3d.visualization.draw_geometries([mesh])


if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description='color obj viewer')
    # parser.add_argument('obj', type=str,                         
    #                     help='obj file path')

    # args = parser.parse_args()

    file_dir = "../output"
    good_list = ["a/20200416035912.obj", "a/20200416035914.obj",
                "b/20200416040037.obj", "b/20200416040133.obj", "b/20200416040213.obj",
                "c/20200416040531.obj", "c/20200416040604.obj", "c/20200416040638.obj"]


    back_list = ["b/20200416040234.obj", "b/20200416040119.obj", 
                "c/20200416040630.obj", "c/20200416040646.obj"]            
    
    # for obj in good_list:
    #     render(os.path.join(file_dir, obj))

    for obj in back_list:
        render(os.path.join(file_dir, obj))
  
    



