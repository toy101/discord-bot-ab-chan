import json

"""
チームタグのセッティング
"""

A_TAG = "A"
B_TAG = "B"
END_MARK = ":"

"""
"""
def make_json():
    
    data = {
        "a_tag" : A_TAG,
        "b_tag" : B_TAG,
        "end_mark" : END_MARK
    }

    with open("./setting.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("update setting.json.")

if __name__ == "__main__":
    make_json()