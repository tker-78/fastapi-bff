# FastAPI BFF

このレポジトリはFastAPI, Keycloakを用いた堅牢な認証認可機能のボイラープレートを提供します。

## 起動方法

```
cp backend/.env.sample backend/.env
```

```
docker compose up --build -d
```

## サービス

- FastAPI: `localhost:8000`
- Keycloak: `localhost:8080`
- Vue.js: `localhost:5173`


## Keycloakの設定

KeycloakのAdmin Console(デフォルトではusername: admin, password: admin)から下記の設定を行う。

- Realm: local-devを新規作成
- Client: fastapi-client(Confidential)を新規作成

![Pasted image 20251203064902.png](docs/Pasted%20image%2020251203064902.png)

![Pasted image 20251203064917.png](docs/Pasted%20image%2020251203064917.png)

![Pasted image 20251203065343.png](docs/Pasted%20image%2020251203065343.png)

.envにClient secretを入力する

※ 現在の構成では.envをimport時に読み込むため、  
   環境変数を変更した場合は、`docker compose  --build api -d`を使用してください。

