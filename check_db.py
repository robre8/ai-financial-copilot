import os
from sqlalchemy import create_engine, text

TEST_DATABASE_URL = os.getenv(
    'TEST_DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/ai_copilot'
)

print(f'✅ TEST_DATABASE_URL: {TEST_DATABASE_URL}')
print(f'✅ Contains postgresql: {"postgresql" in TEST_DATABASE_URL}')

try:
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={'timeout': 5})
    with test_engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
    print('✅ PostgreSQL connected successfully')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('Falling back to SQLite')
