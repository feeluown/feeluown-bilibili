from fuo_bilibili.api.schema.responses import NavInfoResponse


def test_nav_info_response_accepts_current_wallet_and_level_types():
    payload = {
        "code": 0,
        "message": "0",
        "ttl": 1,
        "data": {
            "isLogin": True,
            "face": "https://example.com/avatar.jpg",
            "mid": 123456,
            "uname": "tester",
            "wallet": {
                "bcoin_balance": 3.1,
                "coupon_balance": 0,
            },
            "level_info": {
                "current_level": 6,
                "current_min": 0,
                "current_exp": 100,
                "next_exp": 28800,
            },
            "wbi_img": {
                "img_url": "https://i0.hdslb.com/bfs/wbi/image.png",
                "sub_url": "https://i0.hdslb.com/bfs/wbi/sub.png",
            },
        },
    }

    if hasattr(NavInfoResponse, "model_validate"):
        response = NavInfoResponse.model_validate(payload)
    else:
        response = NavInfoResponse.parse_obj(payload)

    assert response.data.wallet.bcoin_balance == 3.1
    assert response.data.level_info.next_exp == 28800
