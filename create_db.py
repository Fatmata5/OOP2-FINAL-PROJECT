import asyncpg
import asyncio

async def main():
    # Connect to default 'postgres' database
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='420027008',
            host='localhost',
            port=5432,
            database='postgres'
        )
        # Create the database
        await conn.execute('CREATE DATABASE SOCIAL_MEDIAL_API')
        print("✅ Database 'SOCIAL_MEDIAL_API' created successfully!")
        await conn.close()
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("ℹ️ Database already exists.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure PostgreSQL is running and credentials are correct.")

asyncio.run(main())