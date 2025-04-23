# FF旅行小程序 - 行程分享模块

本模块提供行程分享和评论相关的API接口，支持创建行程、查看行程列表、查看行程详情、点赞和评论等功能。

## API接口说明

### 行程相关接口

#### 1. 创建行程

- **URL**: `/api/trips/create`
- **方法**: POST
- **权限**: 需要登录
- **请求参数**:

```json
{
  "title": "行程标题",
  "content": "行程内容",
  "design_style": "minimalism"  // 可选值：constructivism, minimalism, modern, vintage
}
```

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "tripId": 1
  }
}
```

#### 2. 获取行程列表

- **URL**: `/api/trips/list`
- **方法**: GET
- **权限**: 需要登录
- **请求参数**:
  - `page`: 页码(可选，默认1)
  - `page_size`: 每页数量(可选，默认10)
  - `mine`: 是否只查看自己的行程(可选，默认0)

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "trips": [
      {
        "id": 1,
        "title": "行程标题",
        "userId": 1,
        "nickname": "用户昵称",
        "avatar": "头像URL",
        "designStyle": "minimalism",
        "createdAt": "2023-06-01 12:34:56",
        "views": 10,
        "likes": 5,
        "commentCount": 2
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

#### 3. 获取行程详情

- **URL**: `/api/trips/detail/<trip_id>`
- **方法**: GET
- **权限**: 无需登录
- **路径参数**:
  - `trip_id`: 行程ID

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "trip": {
      "id": 1,
      "title": "行程标题",
      "content": "行程内容",
      "userId": 1,
      "nickname": "用户昵称",
      "avatar": "头像URL",
      "designStyle": "minimalism",
      "createdAt": "2023-06-01 12:34:56",
      "views": 11,
      "likes": 5,
      "comments": [
        {
          "id": 1,
          "content": "评论内容",
          "userId": 2,
          "nickname": "评论用户",
          "avatar": "头像URL",
          "createdAt": "2023-06-01 13:00:00"
        }
      ]
    }
  }
}
```

#### 4. 点赞行程

- **URL**: `/api/trips/like`
- **方法**: POST
- **权限**: 需要登录
- **请求参数**:

```json
{
  "trip_id": 1
}
```

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "likes": 6
  }
}
```

### 评论相关接口

#### 1. 添加评论

- **URL**: `/api/trips/comment/add`
- **方法**: POST
- **权限**: 需要登录
- **请求参数**:

```json
{
  "trip_id": 1,
  "content": "评论内容"
}
```

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "commentId": 1,
    "nickname": "用户昵称",
    "avatar": "头像URL",
    "createdAt": "2023-06-01 14:00:00"
  }
}
```

#### 2. 删除评论

- **URL**: `/api/trips/comment/delete/<comment_id>`
- **方法**: DELETE
- **权限**: 需要登录（只能删除自己的评论，管理员例外）
- **路径参数**:
  - `comment_id`: 评论ID

- **返回示例**:

```json
{
  "code": 0,
  "data": {
    "success": true
  }
}
```

## 错误码说明

- `0`: 成功
- `-1`: 参数错误或服务器内部错误
- `-2`: 未授权访问或令牌无效
- `-3`: 权限不足

## 权限说明

- 普通用户(`user`)：可以创建行程、添加评论、删除自己的评论
- 会员用户(`member`)：同普通用户
- 管理员(`admin`)：可以删除任何评论

## 认证方式

所有需要认证的接口，需要在请求头中添加：

```
Authorization: Bearer {token}
```

其中`{token}`为登录接口返回的token值。