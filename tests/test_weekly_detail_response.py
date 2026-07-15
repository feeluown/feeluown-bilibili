from datetime import timedelta

from fuo_bilibili.api.schema.responses import WeeklyDetailResponse


def test_weekly_detail_response_accepts_missing_short_links():
    payload = {
        "code": 0,
        "message": "0",
        "ttl": 1,
        "data": {
            "list": [
                {
                    "aid": 1,
                    "videos": 1,
                    "tid": 17,
                    "tname": "单机游戏",
                    "copyright": 1,
                    "pic": "https://example.com/cover.jpg",
                    "title": "weekly item",
                    "duration": 123,
                    "rights": {
                        "bp": 0,
                        "elec": False,
                        "download": True,
                        "movie": False,
                        "pay": False,
                        "hd5": True,
                        "no_reprint": False,
                        "autoplay": True,
                        "ugc_pay": False,
                        "is_cooperation": False,
                        "ugc_pay_preview": False,
                        "no_background": False,
                        "arc_pay": False,
                    },
                    "owner": {
                        "mid": 123,
                        "name": "owner",
                        "face": "https://example.com/face.jpg",
                    },
                    "stat": {
                        "aid": 1,
                        "view": 10,
                        "danmaku": 2,
                        "like": 3,
                    },
                    "dynamic": "",
                    "cid": 456,
                    "dimension": {
                        "width": 1920,
                        "height": 1080,
                        "rotate": 0,
                    },
                    "first_frame": "https://example.com/frame.jpg",
                    "pub_location": "",
                    "bvid": "BV1xx411c7mD",
                    "rcmd_reason": "",
                }
            ]
        },
    }

    if hasattr(WeeklyDetailResponse, "model_validate"):
        response = WeeklyDetailResponse.model_validate(payload)
    else:
        response = WeeklyDetailResponse.parse_obj(payload)

    item = response.data.list[0]
    assert item.short_link == ""
    assert item.short_link_v2 == ""
    assert item.duration == timedelta(seconds=123)
