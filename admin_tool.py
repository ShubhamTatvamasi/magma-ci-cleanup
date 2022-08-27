"""
Copyright 2020 The Magma Authors.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import json
import os
import sys
import time

from firebase_admin import credentials, db, initialize_app, storage

# load config for creds from file
config = {}
with open("serviceAccountKey.json") as config_file:
    config = json.load(config_file)

# initialize creds
cred = credentials.Certificate(config)
initialize_app(
    cred, {
        'databaseURL': 'https://magma-ci-default-rtdb.firebaseio.com/',
        'storageBucket': 'magma-ci.appspot.com'
    },
)

# get reference to realtime DB
ref = db.reference('/')

#remove workloads older than 3 days
old_date = int(time.time()) - 3 * 24 * 60 * 60
print("Remove all workloads older than ", old_date)

#########  these workloads are no longer being generated

# workloads = ref.child("workers").child("fb_lab_spirent").child("workloads").get()
# if workloads:
#     for key, val in workloads.items():
#         if val.get("state") != "queued" or val.get("timestamp") < old_date:
#             print("##### removing fb_lab_spirent workload", key)
#             ref.child("workers").child("fb_lab_spirent").child("workloads").child(key).set({})

# workloads = ref.child("workers").child("fb_lab_tvm").child("workloads").get()
# if workloads:
#     for key, val in workloads.items():
#         if val.get("state") != "queued" or val.get("timestamp") < old_date:
#             print("##### removing fb_lab_tvm workload", key)
#             ref.child("workers").child("fb_lab_tvm").child("workloads").child(key).set({})

workloads = ref.child("workers").child("wl_lab_5g").child("workloads").get()
if workloads:
    for key, val in workloads.items():
        if val.get("state") != "queued" or val.get("timestamp") < old_date:
            print("###### removing wl_lab_5g workload", key)
            ref.child("workers").child("wl_lab_5g").child("workloads").child(key).set({})



#remove builds and reports older than a month
old_date = int(time.time()) - 30 * 24 * 60 * 60
print("remove all builds and reports older than ", old_date)

#remove all builds older than a month on master
builds = ref.child("builds").get()
#print(builds)
for key, val in builds.items():
    if (val.get("metadata").get("github:ref") == "refs/heads/master") and (val.get("metadata").get("timestamp") < old_date):
        print("##### removing build", key, val.get("metadata").get("timestamp"), val.get("metadata").get("github:ref"))
        ref.child("builds").child(key).set({})


builds = ref.child("builds").get()
reports = ref.child("workers").child("fb_lab_spirent").child("reports").get()
for key, val in reports.items():
    if key not in builds:
        print("##### removing fb_lab_spirent report", key, val.get("timestamp"))
        ref.child("workers").child("fb_lab_spirent").child("reports").child(key).set({})

reports = ref.child("workers").child("fb_lab_tvm").child("reports").get()
for key, val in reports.items():
    if key not in builds:
        print("##### removing fb_lab_tvm report", key, val.get("timestamp"))
        ref.child("workers").child("fb_lab_tvm").child("reports").child(key).set({})

reports = ref.child("workers").child("wl_lab_5g").child("reports").get()
for key, val in reports.items():
    if key not in builds:
        print("##### removing wl_lab_5g report", key, val.get("timestamp"))
        ref.child("workers").child("wl_lab_5g").child("reports").child(key).set({})

reports = ref.child("workers").child("lte_integ_test").child("reports").get()
for key, val in reports.items():
    if key not in builds:
        print("##### removing lte_integ_test report", key, val.get("timestamp"))
        ref.child("workers").child("lte_integ_test").child("reports").child(key).set({})

reports = ref.child("workers").child("cwf_integ_test").child("reports").get()
for key, val in reports.items():
    if key not in builds:
        print("##### removing cwf_integ_test report", key, val.get("timestamp"))
        ref.child("workers").child("cwf_integ_test").child("reports").child(key).set({})


# Remove files that dont have a build present
print("Remove files that dont have a build present")

bucket = storage.bucket()
blobs = list(bucket.list_blobs())

builds = ref.child("builds").get()

for blob in blobs:
    build_name = blob.name[-45:-5]
    print(build_name)
    if build_name not in builds:
        print("********************************** Deleting file")
        bucket.delete_blob(blob.name)
        # count = count + 1
