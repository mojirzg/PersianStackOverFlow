import config
import dataset
conn = dataset.connect('postgresql://postgres:%s@localhost:5432/postgres', config.dbpassword)
print("database connection OK...")

