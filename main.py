import Anomaly
import DB
import Delete_old
user_size = DB.user_size()

# old file delete
Delete_old.delete_old_files()
Anomaly.prediction()



