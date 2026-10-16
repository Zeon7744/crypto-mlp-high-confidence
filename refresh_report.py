"""crypto-mlp 数据刷新：CoinGecko 免费源拉行情 → 写 models/last_refresh.json。CI/本地可跑。"""
import os
import json
import datetime
import urllib.request


def fetch_coingecko():
    try:
        url = ("https://api.coingecko.com/api/v3/simple/price"
               "?ids=bitcoin,ethereum,solana&vs_currencies=usd,cny")
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print("[warn] CoinGecko 拉取失败，回退占位：", e)
        return None


def main():
    os.makedirs("models", exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    data = fetch_coingecko()
    payload = {"ts": ts, "source": "coingecko" if data else "placeholder",
               "prices": data or {"note": "CoinGecko 不可用，占位"}}
    json.dump(payload, open("models/last_refresh.json", "w"), indent=2)
    print("refresh @", ts, "source=", payload["source"])


if __name__ == "__main__":
    main()
