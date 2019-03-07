'''
IP List
'''

s1_ip_list = ['192.128.1.1','192.128.1.2','192.128.1.3','192.168.1.4','192.168.1.5']

s2_ip_list = ['192.128.2.1','192.128.2.2','192.128.2.3','192.168.2.4','192.168.2.5']

s3_ip_list = ['192.128.3.1','192.128.3.2','192.128.3.3','192.168.3.4','192.168.3.5']


s1_ports = [21,22,23,25,80]
s2_ports = [21,22,23,25,80]
s3_ports = [21,22,23,25,80]
other_ports = [1599,8080,2233,8088]


k1 = s1_ports
k2 = s2_ports + other_ports
k3 = s3_ports + other_ports


s1_dst_list = s2_ip_list +s3_ip_list
s2_dst_list = s1_ip_list +s3_ip_list
s3_dst_list = s2_ip_list +s1_ip_list
