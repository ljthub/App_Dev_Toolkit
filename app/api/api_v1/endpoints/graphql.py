from fastapi import APIRouter, Depends
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Annotated, Optional

from schemas.graphql import schema
from core.security import get_current_active_user

# 創建 GraphQL 路由處理器
router = GraphQLRouter(schema)

@router.get("/playground", tags=["GraphQL"])
async def graphql_playground():
    """GraphQL Playground 介紹頁面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphQL Playground</title>
        <meta charset="utf-8">
        <meta name="viewport" content="user-scalable=no, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, minimal-ui">
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
        <link rel="shortcut icon" href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
        <script src="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
    </head>
    <body>
        <div id="root">
            <style>
                body {
                    background-color: rgb(23, 42, 58);
                    font-family: Open Sans, sans-serif;
                    height: 90vh;
                }
                #root {
                    height: 100%;
                    width: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .loading {
                    font-size: 32px;
                    font-weight: 200;
                    color: rgba(255, 255, 255, .6);
                    margin-left: 20px;
                }
                img {
                    width: 78px;
                    height: 78px;
                }
                .title {
                    font-weight: 400;
                }
            </style>
            <img src='//cdn.jsdelivr.net/npm/graphql-playground-react/build/logo.png' alt=''>
            <div class="loading">
                <span class="title">GraphQL Playground</span>
            </div>
        </div>
        <script>
            window.addEventListener('load', function (event) {
                const loadingWrapper = document.getElementById('root');
                loadingWrapper.classList.add('playgroundIn');
                const endpoint = window.location.protocol + '//' + window.location.host + '/api/v1/graphql';
                GraphQLPlayground.init(document.getElementById('root'), {
                    endpoint: endpoint
                });
            });
        </script>
    </body>
    </html>
    """
    return html_content 