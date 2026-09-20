# JanSeva AI — Security & Authentication Architecture

This document provides a comprehensive security specification for the JanSeva AI Citizen Welfare & Scheme Intelligence Platform. It outlines implemented controls, authorization models, multi-factor authentication (MFA) mechanisms, identity privacy guidelines, and recommended production hardening practices.

---

## 1. Authentication Architecture

### Implemented Controls
- **Secure Password Hashing**: Passwords are hashed using `bcrypt` via the `passlib` cryptocontext. Plaintext passwords are never logged, stored, or transmitted in server logs.
- **Short-Lived JWT Tokens**: Authentication relies on JSON Web Tokens (JWT) signed with `HS256` using a secret key. Access tokens have strict expiration policies.
- **MFA Session Isolation**: During authentication or sign-up, the system issues a short-lived `mfa_pending` token (5-minute expiration) that is restricted exclusively to TOTP code confirmation endpoints and cannot be used to access protected citizen endpoints.
- **Password Strength Policy**: Enforces a minimum length requirement of 6 characters (recommended 12+ in production).

---

## 2. Real TOTP Multi-Factor Authentication (MFA)

### Implemented Controls
- **Authenticator App Compatibility**: Supports standard RFC 6238 Time-Based One-Time Passwords (TOTP) compatible with Google Authenticator, Microsoft Authenticator, and Authy.
- **QR Code & Secret Provisioning**: Generates base32 secret keys (`pyotp.random_base32()`) and dynamic QR code image payloads (`data:image/png;base64,...`) for instant scanning.
- **Enrollment Confirmation**: Requires explicit verification of a 6-digit TOTP code before activating `is_mfa_enabled = True` on the user account.
- **Cryptographic Recovery Codes**: Generates 8 single-use, 16-character hex recovery codes for emergency account restoration. Used recovery codes are automatically invalidated and removed from storage.

---

## 3. Server-Side Authorization & IDOR Protection

### Implemented Controls
- **No Anonymous Access**: Anonymous or guest fallback access to personalized citizen profiles, welfare journeys, document uploads, or applications is strictly disabled.
- **Strict Endpoint Verification**: All protected backend endpoints utilize FastAPI dependencies (`get_current_user`) to decode the JWT token, verify token type (`access`), and look up the verified account in the database.
- **Insecure Direct Object Reference (IDOR) Prevention**: Resource endpoints (e.g., `/applications/{application_id}`) verify that `Application.user_id == current_user.id` before returning or mutating application data.

---

## 4. Role-Based Access Control (RBAC) & Admin Separation

### Implemented Controls
- **Role Enforcement**: User accounts are categorized into `CITIZEN` and `ADMIN` roles.
- **Admin Endpoint Protection**: Administrative routes (`/admin/*`), including system analytics, G.O. PDF ingestion, and myScheme catalog synchronization (`/admin/trigger-myscheme-sync`), are protected strictly by `get_current_admin` which rejects citizen access with HTTP 403 Forbidden.
- **Backend Authority**: Role assignment is managed on the backend and cannot be manipulated by frontend client variables.

---

## 5. Document Intelligence & Data Privacy

### Implemented Controls
- **Privacy Disclosure**: A prominent trust badge (`🔒 Your information is protected`) provides citizens with transparent explanations of data collection, local session handling, and non-government endorsement disclaimers.
- **Structured Field Parsing**: Document OCR parses key fields (Full Name, Date of Birth, Annual Income, District) with confidence scores and verification states (`verified`, `verify_warning`, `unconfirmed`) instead of dumping raw OCR text.
- **Document Access Control**: Uploaded document files are stored securely and accessible only by the verified owning account or authorized administrative services.

---

## 6. Implementation Summary

| Security Feature | Implemented in Prototype | Recommended for Production |
| :--- | :---: | :---: |
| **Bcrypt Password Hashing** | ✅ | ✅ |
| **TOTP Authenticator MFA** | ✅ | ✅ |
| **Recovery Codes** | ✅ | ✅ |
| **Server-Side IDOR Checks** | ✅ | ✅ |
| **Citizen vs Admin RBAC** | ✅ | ✅ |
| **3-Language Localization** | ✅ | ✅ |
| **HTTPS / TLS Transport** | ⚠️ (Local HTTP) | ✅ (Mandatory HTTPS) |
| **HttpOnly SameSite Cookies** | ⚠️ (Session Token) | ✅ (Strict Cookies) |
| **Rate Limiting / Lockout** | ⚠️ (Basic) | ✅ (Redis-backed Rate Limiter) |
| **Pretrained Vision-Language AI** | ✅ (OCR + Heuristic AI) | ✅ (Dedicated Document AI) |

---

## 7. Production Hardening Recommendations

1. **Enforce HTTPS/TLS**: Deploy backend and frontend services behind reverse proxies (Nginx/Traefik) enforcing TLS 1.3 encryption.
2. **HttpOnly Cookies**: Transition JWT token delivery to `HttpOnly`, `Secure`, `SameSite=Strict` cookies to prevent XSS token theft.
3. **Rate Limiting**: Implement Redis-backed sliding window rate limiting on `/auth/login`, `/auth/mfa/verify`, and `/auth/register` to block brute-force attacks.
4. **Step-Up MFA**: Require re-authentication for sensitive actions such as password changes, email updates, or MFA secret reset.
