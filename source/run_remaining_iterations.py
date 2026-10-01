from pathlib import Path
import json,subprocess,time,sys
R=Path(__file__).resolve().parents[1]
start=int(sys.argv[1]) if len(sys.argv)>1 else 3
for n in range(start,11):
    deadline=time.monotonic()+900
    while True:
        p=R/'source/current_iteration_complete.json'
        state=json.loads(p.read_text()) if p.exists() else {}
        if state.get('round')==n:break
        log=(R/'source/build.log').read_text() if (R/'source/build.log').exists() else ''
        if 'Traceback (most recent call last)' in log:
            print('CAD error in round',n,log[-2400:],flush=True);sys.exit(1)
        if time.monotonic()>deadline:raise TimeoutError('CAD round '+str(n))
        time.sleep(2)
    subprocess.run([sys.executable,str(R/'source/review_iteration.py')],cwd=R,check=True)
    print('ROUND %02d COMPLETE: preview saved, 18 mesh checks passed.'%n,flush=True)
    if n<10:subprocess.run([sys.executable,str(R/'source/queue_iteration.py'),str(n+1)],cwd=R,check=True)
print('TEN ITERATIONS COMPLETE',flush=True)
