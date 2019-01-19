'''
IP List
'''

s1_ip_list = ['192.128.1.1','192.128.1.2','192.128.1.3']

s2_ip_list = ['192.128.2.1','192.128.2.2','192.128.2.3']

s3_ip_list = ['192.128.3.1','192.128.3.2','192.128.3.3']

s4_ip_list = ['192.128.4.1','192.128.4.2','192.128.4.3']

s5_ip_list = ['192.128.5.1','192.128.5.2','192.128.5.3']

s1_ports = [21,22,23,25,80]
s2_ports = [21,22,23,25,80]
s3_ports = [21,22,23,25,80]
s4_ports = [21,22,23,25,80]
s5_ports = [21,22,23,25,80]
other_ports = [1599,8080,2233,8088]


k1 = s1_ports
k2 = s2_ports + other_ports
k3 = s3_ports + other_ports
k4 = s4_ports + other_ports
k5 = s5_ports + other_ports

s1_dst_list = s2_ip_list +s3_ip_list + s4_ip_list + s5_ip_list
s2_dst_list = s1_ip_list +s3_ip_list + s4_ip_list + s5_ip_list
s3_dst_list = s2_ip_list +s1_ip_list + s4_ip_list + s5_ip_list
s4_dst_list = s2_ip_list +s3_ip_list + s1_ip_list + s5_ip_list
s5_dst_list = s2_ip_list +s3_ip_list + s4_ip_list + s1_ip_list
