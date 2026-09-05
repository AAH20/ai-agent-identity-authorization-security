package agentiam.authorization

default allow := false

allow if {
  input.identity.type == "ai_agent"
  input.identity.agent_id != ""
  input.delegation.active == true
  input.delegation.expires_at_ns > time.now_ns()
  input.request.audience == input.token.audience
  input.request.resource in input.delegation.resources
  input.request.action in input.delegation.actions
  input.request.resource == input.token.resource
  input.request.action in input.token.actions
  input.token.proof_of_possession_verified == true
  not input.context.prompt_injection_detected
}

requires_approval if {
  input.request.action in {"write", "execute", "delete", "risk_accept"}
}

deny_reason contains "inactive delegation" if not input.delegation.active
deny_reason contains "prompt injection signal" if input.context.prompt_injection_detected
deny_reason contains "proof of possession missing" if not input.token.proof_of_possession_verified
deny_reason contains "resource outside delegation" if not input.request.resource in input.delegation.resources
deny_reason contains "action outside delegation" if not input.request.action in input.delegation.actions
