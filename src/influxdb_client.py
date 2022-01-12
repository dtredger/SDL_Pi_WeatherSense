from influxdb import InfluxDBClient

def format_point(measurement, timestamp, device_id, field_val):
    return {
        "measurement": measurement,
        "time": timestamp,
        "tags": {
            "device_id": device_id
        },
        "fields": {
            'value': field_val
        }
    }

def insert_records(database, records_arr):
    client = InfluxDBClient(database=database)
    # client.create_database(database)
    return client.write_points(records_arr)


# --- --- --- --- --- ---
#
# # import from file
# def read_data(filename, headers=False):
#     with open(filename) as f:
#         # split on tab
#         if headers:
#             headers = [x.split('	') for x in f.readlines()[:1]][0]
#             data = [x.split('\t') for x in f.readlines()[1:]]
#             return headers, data
#         else:
#             return [], [x.split('\t') for x in f.readlines()[1:]]



# https://influxdb-python.readthedocs.io/en/latest/resultset.html
# result_set = client.query(f"select * from {measurement};")
# list(rs.get_points(measurement))
# list(rs.get_points(tags={'deviceID':'187'}))


# ---- ---- ----


# filename = 'indoor_temp.txt'
# headers, data = read_data(filename)
# headers = ['id', 'TimeStamp', 'DeviceID', 'ChannelID', 'Temperature', 'Humidity', 'BatteryOK', 'TimeRead']
#
# for line in data[:5]:
#     device_id = line[2]
#     temp = line[4]
#     humidity = line[5]
#     timestamp = line[-1]
#     temp_record = new_indoor_record('temperature', timestamp, device_id, temp)
#     humidity_record = new_indoor_record('humidity', timestamp, device_id, humidity)
#     client.write_points([temp_record, humidity_record])
