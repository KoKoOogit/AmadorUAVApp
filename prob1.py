
import matplotlib.pyplot as plt
import random
import numpy as np

def find_theta(corner_points):
    sort_y = np.argsort(corner_points[:,1])
    # get the smallest two  piars with smallest y cordinates
#     a,b = corner_points[sort_y[0]], corner_points[sort_y[1]]
    a,b = corner_points[1],corner_points[2]
    
    a_b_arr =np.array([a,b])
    is_oriented_counterclockwise = False
    
    min_x = np.min(a_b_arr[:,0])
    max_x = np.max(a_b_arr[:,0] )
    min_y = np.min(a_b_arr[:,1])
    max_y = np.max(a_b_arr[:,1])
    try:
        slope = (a[1]-b[1])/(a[0]-b[0])
    except ZeroDivisionError:
        return 0,0, False

    if slope < 0:
            # If the slope is negetive it is tilting positive
            missing_point = [min_x,min_y]
            x_distance = max_x - missing_point[0]
            y_distance = max_y - missing_point[1]
            theta = np.degrees(np.arctan2(y_distance,x_distance))
            beta = np.degrees(np.arctan2(x_distance,y_distance)) 



          
          
    if slope > 0:
         # If the slope is positive 
        missing_point = [max_x,min_y]
        x_distance = missing_point[0] - min_x
        y_distance = max_y - missing_point[1]
 
    
        theta = np.degrees(np.arctan2(y_distance,x_distance)) 
        beta = np.degrees(np.arctan2(x_distance,y_distance)) 
        is_oriented_counterclockwise = True

        
    return missing_point, theta, is_oriented_counterclockwise

def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    return 1 if val > 0 else 2

def graham_scan(points):
    n = len(points)
    if n < 3:
        return []

    pivot_idx = np.argmin(points, axis=0)[1]
    pivot = points[pivot_idx]
    
    angles = np.arctan2(points[:, 1] - pivot[1], points[:, 0] - pivot[0])
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]

    hull = [sorted_points[0], sorted_points[1], sorted_points[2]]

    for i in range(3, n):
        while len(hull) > 1 and orientation(hull[-2], hull[-1], sorted_points[i]) != 2:
            hull.pop()
        hull.append(sorted_points[i])

    return np.array(hull)

def read_points_from_file(filename):
    try:
        with open(filename, 'r') as file:
            N = int(file.readline().strip())
            points = []

            for _ in range(N):
                x, y = map(int, file.readline().strip().split())
                points.append([x, y])

            points_array = np.array(points)
            return points_array
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


filename = "box.in"  
points = read_points_from_file(filename)



def get_rotating_caliper_bbox_list(hull_points_2d):
    smallest_area = np.inf
    smallest_angle = 91
    """
    hull_points_2d: array of hull points. each element should have [x,y] format
    """
    # Compute edges (x2-x1,y2-y1)
    edges = np.zeros( (len(hull_points_2d)-1,2) ) 
    for i in range( len(edges) ):
        edge_x = hull_points_2d[i+1,0] - hull_points_2d[i,0]
        edge_y = hull_points_2d[i+1,1] - hull_points_2d[i,1]
        edges[i] = [edge_x,edge_y]
    # Calculate edge angles   atan2(y/x)
    edge_angles = np.zeros( (len(edges)) ) 
    for i in range( len(edge_angles) ):
        edge_angles[i] = np.arctan2( edges[i,1], edges[i,0] )
    # Check for angles in 1st quadrant
    for i in range( len(edge_angles) ):
        edge_angles[i] = np.abs( edge_angles[i] % (np.pi/2) ) 


    edge_angles = np.unique(edge_angles)

    bbox_list= None
    for i in range( len(edge_angles) ):
    
        R = np.array([ [ np.cos(edge_angles[i]), np.cos(edge_angles[i]-(np.pi/2)) ], [ np.cos(edge_angles[i]+(np.pi/2)), np.cos(edge_angles[i]) ] ])

        rot_points = np.dot(R, np.transpose(hull_points_2d) ) 

        min_x = np.nanmin(rot_points[0], axis=0)
        max_x = np.nanmax(rot_points[0], axis=0)
        min_y = np.nanmin(rot_points[1], axis=0)
        max_y = np.nanmax(rot_points[1], axis=0)
    
        width = max_x - min_x
        height = max_y - min_y
        area = width*height
        
        center_x = (min_x + max_x)/2
        center_y = (min_y + max_y)/2
        center_point = np.dot( [ center_x, center_y ], R )
  
        corner_points = np.zeros( (4,2) ) 
        corner_points[0] = np.dot( [ max_x, min_y ], R )
        corner_points[1] = np.dot( [ min_x, min_y ], R )
        corner_points[2] = np.dot( [ min_x, max_y ], R )
        corner_points[3] = np.dot( [ max_x, max_y ], R )
        c2, c1 = corner_points[2],corner_points[1]

        missing_point,angle,is_oriented_clockwise = find_theta(corner_points)
        bbox_info = [angle, area, (width, height),( min_x, max_x, min_y, max_y, corner_points, center_point),missing_point]
        
        if area < smallest_area:
            if is_oriented_clockwise:
                bbox_info[0] = bbox_info[0] * -1
            bbox_list = bbox_info
           
                    
        if area == smallest_area:
            if is_oriented_clockwise:
                bbox_info[0] = bbox_info[0] * -1

            if angle < smallest_angle:
                smallest_angle = angle
                bbox_list = bbox_info


                
    return bbox_list
#Doesn't need this 
def plot_bounding_box(hull_points_2d, bbox_info):
    fig, ax = plt.subplots()

   
    angle, area, (width, height), (min_x, max_x, min_y, max_y, corner_points, center_point),missing_point = bbox_info
 
    for i in range(4):
        plt.plot([corner_points[i, 0], corner_points[(i+1) % 4, 0]], [corner_points[i, 1], corner_points[(i+1) % 4, 1]],color="red")
        plt.scatter(corner_points[i,0],corner_points[i,1], label=f"c {i}")
    # Plot the center point
    plt.plot(center_point[0], center_point[1], 'go', label='Center')
    plt.scatter(points[:,0],points[:,1],label="points")
    plt.scatter(missing_point[0],missing_point[1],label="Missing Point", color="gray")
    # Set axis limits for better visualization
    

    plt.gca().set_aspect('equal')
    plt.legend()
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Smallest Bounding Box (Area: {area:.2f}, Angle: {angle} degrees)')
    plt.grid()
    plt.show()

def random_points(N):
    points = np.array([[random.randint(-10,10) for i in range(2)] for i in range(N)])
    return points    


#using them
# points_r = random_points(10)
hull_points = graham_scan(points)
bbox = get_rotating_caliper_bbox_list(hull_points)

angle, area, (width, height),( min_x, max_x, min_y, max_y, corner_points, center_point),missing_point = bbox
f = open("box.out", "a")
f.write( f"{np.round(angle,2)} {np.round(area,2)}")
f.close()
