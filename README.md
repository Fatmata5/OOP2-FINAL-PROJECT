# Social Media Post API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-4169E1?logo=postgresql)](https://www.postgresql.org)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production‑ready REST API for social media platforms – posts, comments, likes, and JWT authentication.  
Built with **FastAPI**, **async SQLAlchemy**, **PostgreSQL**, and aligned with **SDG 8 (Decent Work & Economic Growth)**.

---

## 📋 Table of Contents

- [Requirements Fulfilled](#requirements-fulfilled)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Async I/O Demonstration](#async-io-demonstration)
- [SDG 8 Alignment](#sdg-8-alignment)
- [Testing](#testing)
- [Collaboration & Open Source](#collaboration--open-source)
- [License](#license)
- [Authors](#authors)

---

## ✅ Requirements Fulfilled

| Requirement                          | Implementation |
|--------------------------------------|----------------|
| FastAPI framework                    | ✅ `main.py` |
| CRUD operations (posts/comments/likes) | ✅ |
| PostgreSQL + SQLAlchemy (async)      | ✅ `database.py`, `models.py` |
| Dependency injection for DB sessions | ✅ `Depends(get_db)` |
| OAuth2 + JWT authentication          | ✅ `auth.py` |
| REST standards (HTTP methods, status codes) | ✅ |
| Automatic Swagger UI (`/docs`) & ReDoc (`/redoc`) | ✅ |
| Async I/O task (external API call)   | ✅ `/posts/{id}/analyze` |
| Python type hints                    | ✅ all files |
| SDG alignment (SDG 8 – Decent Work)  | ✅ `/sdg` endpoint |
| Open‑source license (MIT)            | ✅ `LICENSE` |
| GitHub collaboration (issues, PRs, branches) | ✅ |

---

## 🧰 Tech Stack

- **Framework** – FastAPI  
- **Database** – PostgreSQL (asyncpg driver)  
- **ORM** – SQLAlchemy 2.0 (asynchronous)  
- **Authentication** – OAuth2 password flow, JWT, bcrypt  
- **Validation** – Pydantic v2  
- **Async I/O demo** – httpx + asyncio  

---

## 📁 Project Structure
