from django.http import JsonResponse, HttpResponse
from BlogsData.utils import get_db_handle
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


def configure_db(db_name="blogsData"):
    return get_db_handle(
        db_name=db_name, host="localhost", port="27017", username="", password=""
    )


def list_collections(request):
    db_handle, client = configure_db()
    collections = db_handle.list_collection_names()
    return JsonResponse({"collections": collections, "client": str(client)})


def list_all_users(request):
    list_users = []
    db_handle, client = configure_db()
    users = db_handle.get_collection("users").find({}, {"_id": False})
    for user in users:
        print(user)
        list_users.append(user)
    return JsonResponse({"users": list_users, "client": str(client)})


def list_all_blogs(request):
    list_blogs = []
    db_handle, client = configure_db()
    blogs = db_handle.get_collection("blogs").find({}, {"_id": False})
    for blog in blogs:
        print(blog)
        list_blogs.append(blog)
    return JsonResponse({"blogs": list_blogs, "client": str(client)})


def list_all_comments(request):
    list_comments = []
    db_handle, client = configure_db()
    comments = db_handle.get_collection("comments").find({}, {"_id": False})
    for comment in comments:
        print(comment)
        list_comments.append(comment)
    return JsonResponse({"comments": list_comments, "client": str(client)})


def get_details_by_user(request, username):
    db_handle, client = configure_db()
    pipeline = [
        {"$match": {"username": username}},
        {
            "$lookup": {
                "from": "comments",
                "localField": "_id",
                "foreignField": "author",
                "as": "user_comments",
                "pipeline": [{"$project": {"_id": 0, "comment": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "blogs",
                "localField": "_id",
                "foreignField": "author",
                "as": "blogs",
                "pipeline": [
                    {
                        "$lookup": {
                            "from": "comments",
                            "localField": "_id",
                            "foreignField": "blog",
                            "as": "comments",
                            "pipeline": [
                                {"$project": {"_id": 0, "author": 0, "blog": 0}}
                            ],
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "author": 0,
                        }
                    },
                ],
            },
        },
        {"$project": {"_id": 0}},
    ]

    db_data = db_handle["users"].aggregate(pipeline=pipeline)
    for data in db_data:
        json_data = data
    return JsonResponse(json_data)


@csrf_exempt
def find_stores(request):
    db_handle, client = configure_db()
    if request.method == "POST":
        body = json.loads(request.body)
        longitude = body["location"]["longitude"]
        latitude = body["location"]["latitude"]
        radius_km = body["radius_km"]
        data = db_handle["stores"].count_documents(
            {
                "location": {
                    "$geoWithin": {
                        "$centerSphere": [[longitude, latitude], radius_km*1000/6371.0]
                    }
                }
            }
            # {
            #     "location": {
            #         "$nearSphere": {
            #             "$geometry": {
            #                 "type": "Point",
            #                 "coordinates": [longitude, latitude]
            #             },
            #             "$minDistance": 5,
            #             "$maxDistance": radius_km*1000
            #         }
            #     }
            # }
        )
        return JsonResponse({"store_count": data})
    else:
        return HttpResponse(request, status=405)
