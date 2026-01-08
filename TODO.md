# Yeti: Office Deployment Roadmap (internal-v1)

## 🔐 Phase 1: Authentication & Access
- [ ] **Google Workspace SSO**: Integrate `NextAuth.js` or standard OAuth2 to allow login via company email (`@digitalwallet.co.jp`?).
- [ ] **User Whitelist**: Restrict access to specific domains or user lists.
- [ ] **Session Management**: Ensure `thread_id` is linked to the authenticated user's email/ID in Postgres.

## ⭐ Phase 2: RLHF / Feedback Loop
- [ ] **Rating UI**: Add 1-5 Star rating buttons below every AI response.
- [ ] **Comment Field**: Optional text area for "How can this be improved?".
- [ ] **Feedback Database**: Create a new table `feedback_logs` in Postgres to store:
  - `user_id`
  - `prompt`
  - `response`
  - `rating`
  - `comment`
  - `timestamp`

## 🖥️ Phase 3: Hardware & Deployment (RTX 4060)
- [ ] **Model Selection**: 
  - *Constraint*: RTX 4060 has 8GB VRAM.
  - *Recommendation*: **Mistral Nemo 12B (Q4_K_M)** or **Llama 3 8B (Q5/Q6)**. 
  - *Note*: 70B models will NOT fit on an 8GB card.
- [ ] **Docker GPU Config**: Update `docker-compose.yml` to use NVIDIA runtime.
- [ ] **Load Testing**: Verify how many concurrent users the 4060 can handle (likely 2-3 simultaneous streams before queuing).

## 🛠️ Maintenance & Analytics
- [ ] **Admin Dashboard**: Simple view to see "Top questions asked" and "Average Rating".
- [ ] **Daily Backups**: Automated dump of the Postgres database (Conversations + Feedback).
