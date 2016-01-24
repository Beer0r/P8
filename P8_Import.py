
# coding: utf-8

# Init of numpy, sunpy, astropy, scidb and JSOC

# In[1]:

import csv
import os
import numpy
import astropy
import sunpy
from sunpy.net import jsoc
from astropy.io import fits
from scidbpy import connect, SciDBQueryError, SciDBArray
sdb = connect('http://localhost:8080')
afl = sdb.afl
client = jsoc.JSOCClient()


# Define JSOC Query

# In[9]:

response = client.query(jsoc.Time('2014-01-01T00:00:00', '2014-01-01T01:00:00'), jsoc.Series('hmi.m_45s'), jsoc.Notify("simon.marcin@fhnw.ch"))
print response


# Start download

# In[ ]:

res = client.get(response)


# Create 3D Array to store the images. x-axis, y-axis and time-axis.

# In[2]:

sdb.query("CREATE ARRAY HMI_Cube <val:float>[x=0:4095,512,1, y=0:4095,512,1, time=0:*,1,0]")


# Validate the schema of the created array

# In[25]:

hmi_cube = sdb.wrap_array("HMI_Cube")
print hmi_cube.datashape.schema


# In[ ]:

Get some basic fits information useing astropy.fits


# In[22]:

hdulist = fits.open('/home/scidb/sunpy/data/hmi.m_45s.20140101_000045_TAI.2.magnetogram.fits')
hdulist.info()


# Process all fits file. The time dimension is broken down to an increasing integer. The file 'hmi_cube_import.csv' is a flat array representation of all fits file which gets imported to SciDB.

# In[71]:

f = open('/home/scidb/p8/hmi_cube_import.csv','w')
count=0
for fn in os.listdir("./sunpy/data"):
    if fn.endswith("fits"):
        hdulist = fits.open('/home/scidb/sunpy/data/'+fn)
        hdulist[1].verify('fix')
        scidata = hdulist[1].data
        for x in xrange(0, 4095):
            for y in xrange(0, 4095):
                f.write('%d,%d,%d,%f\n' % (x,y,count,scidata[x][y]))
        print (fn+" done")
        count=count+1
f.close()


# Import the flat data in parallel into the database. (run on direct on bash):
# loadcsv.py -n 1 -a 'aFlat' -s '<x:int64,y:int64,time:int64, val:float> [csvRow=0:*,500000,0]' -i './p8/hmi_cube_import.csv' -A 'HMI_Cube' -S '<val:float> [x=0:4095,512,1,y=0:4095,512,1,time=0:*,1,0]'

# Disconnect from SciDB.

# In[3]:

sdb.reap()

