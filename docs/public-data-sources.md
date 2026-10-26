# 公开数据来源说明

真实岗位直接读取企业通过 Lever 发布的公开招聘信息，保持原始标题、公司、工作地点及描述，页面显示来源链接和采集日期。这里只同步公开岗位，不向企业提交申请、不发布新职位，也不访问其候选人数据。是否仍在招聘、地点限制及具体要求以原始招聘页面为准。

- Palantir：https://jobs.lever.co/palantir
- Spotify：https://jobs.lever.co/spotify
- Lever 官方公开接口文档：https://github.com/lever/postings-api

公开简历来自 JSON Resume 公开接口及本人维护的职业履历。只导入姓名、职业摘要、技能、教育、工作和项目经历；不导入邮箱、电话、住址、头像、第三方评价。内容按来源字段转换，不用 AI 编造背景、年限或技能。它们是职业履历参考资料，不代表本人向本平台投递或正在求职。

- https://registry.jsonresume.org/thomasdavis
- https://registry.jsonresume.org/alifeee
- https://registry.jsonresume.org/nfriend
- https://registry.jsonresume.org/spidiweb
- https://registry.jsonresume.org/ianchanning
- https://registry.jsonresume.org/sshilko
- https://registry.jsonresume.org/mhite
- https://registry.jsonresume.org/jorgeas80
- JSON Resume 官方接口文档：https://registry.jsonresume.org/docs

点击导入时实时获取，一小时内避免重复请求；网络故障、已删除资料及示例人物会被跳过并给出提示，绝不使用虚构数据补位。新账号可自行导入到自己的工作区，其他用户不能直接查看该工作区中的简历。

图片识别使用 RapidOCR 和 ONNX Runtime 在本机执行：https://github.com/RapidAI/RapidOCR 。OCR 结果可能受拍摄角度、分辨率和排版影响，用户可在简历详情的识别原文区核对内容。
