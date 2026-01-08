# kanban-core Specification

## Purpose
TBD - created by archiving change add-kanban-core. Update Purpose after archive.
## Requirements
### Requirement: 项目管理
系统 MUST 提供项目的创建、查看、编辑、删除功能。

#### Scenario: 创建项目成功
- **WHEN** 用户提供有效的项目名称
- **THEN** 系统创建新项目
- **AND** 自动创建默认列（待办、进行中、已完成）
- **AND** 返回项目信息

#### Scenario: 项目名称为空
- **WHEN** 用户提供空的项目名称
- **THEN** 系统返回错误信息"项目名称不能为空"

#### Scenario: 获取项目列表
- **WHEN** 用户请求项目列表
- **THEN** 系统返回当前用户创建的所有项目

#### Scenario: 获取项目详情
- **WHEN** 用户请求指定项目的详情
- **THEN** 系统返回项目信息、所有列及其任务

#### Scenario: 更新项目
- **WHEN** 用户更新项目名称或描述
- **THEN** 系统保存更新后的项目信息

#### Scenario: 删除项目
- **WHEN** 用户删除项目
- **THEN** 系统删除项目及其所有列和任务
- **AND** 返回成功响应

#### Scenario: 访问他人项目
- **WHEN** 用户尝试访问非自己创建的项目
- **THEN** 系统返回403禁止访问错误

### Requirement: 看板列管理
系统 MUST 提供看板列的创建、查看、编辑、删除、排序功能。

#### Scenario: 创建列成功
- **WHEN** 用户在项目中创建新列
- **THEN** 系统创建列并设置为最后位置
- **AND** 返回列信息

#### Scenario: 列名称为空
- **WHEN** 用户提供空的列名称
- **THEN** 系统返回错误信息"列名称不能为空"

#### Scenario: 更新列
- **WHEN** 用户更新列名称
- **THEN** 系统保存更新后的列信息

#### Scenario: 删除列
- **WHEN** 用户删除列
- **THEN** 系统删除列及其所有任务
- **AND** 返回成功响应

#### Scenario: 列排序
- **WHEN** 用户调整列的顺序
- **THEN** 系统更新所有受影响列的位置
- **AND** 返回更新后的列列表

### Requirement: 任务卡片管理
系统 MUST 提供任务卡片的创建、查看、编辑、删除功能。

#### Scenario: 创建任务成功
- **WHEN** 用户在列中创建新任务
- **THEN** 系统创建任务并设置为列的最后位置
- **AND** 返回任务信息

#### Scenario: 任务标题为空
- **WHEN** 用户提供空的任务标题
- **THEN** 系统返回错误信息"任务标题不能为空"

#### Scenario: 更新任务
- **WHEN** 用户更新任务标题
- **THEN** 系统保存更新后的任务信息

#### Scenario: 删除任务
- **WHEN** 用户删除任务
- **THEN** 系统删除任务
- **AND** 返回成功响应

### Requirement: 前端项目列表页
前端 MUST 提供项目列表页面，展示用户的所有项目。

#### Scenario: 展示项目列表
- **WHEN** 用户访问项目列表页
- **THEN** 页面展示所有项目卡片
- **AND** 每个卡片显示项目名称和描述

#### Scenario: 创建新项目
- **WHEN** 用户点击创建项目按钮
- **THEN** 弹出创建项目对话框
- **AND** 用户填写信息后创建项目

#### Scenario: 进入看板视图
- **WHEN** 用户点击项目卡片
- **THEN** 跳转到该项目的看板视图页

### Requirement: 前端看板视图页
前端 MUST 提供看板视图页面，展示项目的列和任务。

#### Scenario: 展示看板视图
- **WHEN** 用户访问看板视图页
- **THEN** 页面横向展示所有列
- **AND** 每列纵向展示其任务卡片

#### Scenario: 添加新列
- **WHEN** 用户点击添加列按钮
- **THEN** 在看板末尾添加新列

#### Scenario: 添加新任务
- **WHEN** 用户在列中点击添加任务按钮
- **THEN** 在该列末尾添加新任务卡片

#### Scenario: 编辑列名称
- **WHEN** 用户双击列标题
- **THEN** 列标题变为可编辑状态
- **AND** 用户可以修改列名称

#### Scenario: 编辑任务标题
- **WHEN** 用户双击任务卡片
- **THEN** 任务标题变为可编辑状态
- **AND** 用户可以修改任务标题

#### Scenario: 删除列确认
- **WHEN** 用户点击删除列按钮
- **THEN** 弹出确认对话框提示将删除列及其所有任务
- **AND** 用户确认后删除列

#### Scenario: 删除任务
- **WHEN** 用户点击任务的删除按钮
- **THEN** 删除该任务

