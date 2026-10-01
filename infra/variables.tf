# 계정 · 리전 · 주소 · 비밀값에는 기본값을 두지 않는다. 잘못된 곳에 조용히 올라가지 않도록

variable "aws_region" {
  description = "파수꾼을 올릴 리전. 우리 스택과 달라도 된다 — 오히려 그래야 같이 죽지 않는다"
  type        = string
}

variable "name_prefix" {
  description = "Lambda · 역할 · 일정 이름의 앞머리"
  type        = string
  default     = "monimo-watchdog"
}

variable "schedule_enabled" {
  description = "일정을 켤지. 조회 문이 들어오기 전에 켜면 1분마다 오탐 Slack 이 하루 1,440번 간다"
  type        = bool
  default     = false
}

variable "schedule_expression" {
  description = "EventBridge Scheduler 주기. 최소 1분"
  type        = string
  default     = "rate(1 minute)"
}

variable "lambda_timeout_sec" {
  description = "한 주기는 2~3초면 끝난다. 주문 10 + 조회 10 + 알림 5 + 핑 5 를 다 쓰는 최악을 덮는 값"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch 로그 보관. 0 이면 무기한이라 명시한다"
  type        = number
  default     = 14
}

variable "shop_order_url" {
  description = "카나리가 traceparent 를 붙여 호출할 쇼핑몰 주문 API"
  type        = string
}

variable "api_server_url" {
  description = "카나리 신선도를 조회할 API 서버"
  type        = string
}

variable "monimo_internal_token" {
  description = "내부 문 출입증. API 서버의 같은 이름 값과 맞춘다"
  type        = string
  sensitive   = true
}

variable "slack_webhook" {
  description = "파수꾼 전용 슬랙 웹훅. 관제 스택(notifier)과 다른 채널"
  type        = string
  sensitive   = true
}

variable "ping_url" {
  description = "Healthchecks.io 핑 주소 (Dead Man's Switch)"
  type        = string
  sensitive   = true
}
