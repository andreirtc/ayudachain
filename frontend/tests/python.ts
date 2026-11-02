import path from 'node:path';

// Use the checkout's locked environment on both supported desktop platforms.
export const python=process.env.MVP_TEST_PYTHON||path.resolve(__dirname,'../../.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
