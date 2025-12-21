import numpy as np
import pandas as pd

def main():
    rng = np.random.default_rng(42)
    n=400
    t=np.arange(n)
    base=50+0.02*t+np.sin(t/18)*2
    noise=rng.normal(0,0.8,size=n)
    y=base+noise
    idx=rng.choice(np.arange(50,n-50),size=16,replace=False)
    y[idx]+=rng.choice([-8,-6,6,9],size=len(idx))
    out=r'data/p11_ticket_triage_automl_data.csv'
    pd.DataFrame({'t':t,'value':y}).to_csv(out,index=False)
    print('OK ->', out)

if __name__=='__main__':
    main()
