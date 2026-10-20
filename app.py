import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone

st.set_page_config(page_title='Maritime Human-AI Teaming Lab',layout='wide')
st.markdown('''<style>
.stApp {background:linear-gradient(130deg,#071725,#102b3b 60%,#071725);color:#e7f3f9}
[data-testid="stMetric"] {background:#102e40;border:1px solid #285168;padding:13px;border-radius:12px}
[data-testid="stSidebar"] {background:#0c2535}
div.stButton>button {border-radius:9px}
</style>''',unsafe_allow_html=True)
st.title('⚓ Maritime Human–AI Teaming Lab')
st.caption('Research prototype · Synthetic traffic · Not for navigation')

if 'log' not in st.session_state: st.session_state.log=[]
if 'tick' not in st.session_state: st.session_state.tick=0
if 'heading' not in st.session_state: st.session_state.heading=0.0
if 'own_pos' not in st.session_state: st.session_state.own_pos=np.array([0.,0.])
if 'history' not in st.session_state: st.session_state.history=[(0.,0.)]
if 'scenario_key' not in st.session_state: st.session_state.scenario_key='Crossing (starboard)'

mode=st.sidebar.radio('Control mode',['Human + AI','Human Only','AI Only'])
scenario=st.sidebar.selectbox('Scenario',['Crossing (starboard)','Head-on','Overtaking'])
noise=st.sidebar.slider('Position uncertainty (m)',0,150,25,5)
step=st.sidebar.slider('Simulation step (seconds)',10,120,30,10)
if st.session_state.scenario_key!=scenario:
    st.session_state.scenario_key=scenario
    st.session_state.tick=0; st.session_state.heading=0.
    st.session_state.own_pos=np.array([0.,0.]);st.session_state.history=[(0.,0.)]
if st.sidebar.button('Reset scenario'):
    st.session_state.tick=0; st.session_state.heading=0.
    st.session_state.own_pos=np.array([0.,0.]);st.session_state.history=[(0.,0.)]
    st.rerun()

# East/North local coordinates in nautical miles. Heading: clockwise from north.
def vel(speed_kn,heading_deg):
    r=np.deg2rad(heading_deg)
    return np.array([speed_kn*np.sin(r),speed_kn*np.cos(r)])/3600.

def target_initial(kind):
    if kind=='Crossing (starboard)': return np.array([2.5,2.5]),225.,14.
    if kind=='Head-on': return np.array([0.,5.]),180.,12.
    return np.array([0.,-2.]),0.,18.

def cpa(own,target,vown,vtarget):
    r=target-own; v=vtarget-vown
    tcpa=max(0.,-float(r@v)/(float(v@v)+1e-12))
    dcpa=float(np.linalg.norm(r+v*tcpa))
    return dcpa,tcpa

own_speed=12.
target0,th,ts=target_initial(scenario)
t=st.session_state.tick
own=st.session_state.own_pos.copy()
target=target0+vel(ts,th)*t
vo=vel(own_speed,st.session_state.heading); vt=vel(ts,th)
dcpa,tcpa=cpa(own,target,vo,vt)
risk=(dcpa<0.5 and tcpa<1800)
# Simplified geometric suggestion, not a COLREG-compliant decision engine.
candidates=[0,15,30,45,-15,-30,-45]
results=[]
for change in candidates:
    new_h=(st.session_state.heading+change)%360
    d,tt=cpa(own,target,vel(own_speed,new_h),vt)
    results.append((change,d,tt))
safe=[r for r in results if r[1]>=0.5]
recommendation=min(safe,key=lambda x:(abs(x[0]),x[0]<0)) if safe else max(results,key=lambda x:x[1])
rec_delta,rec_cpa,rec_tcpa=recommendation

c1,c2,c3,c4=st.columns(4)
c1.metric('Current DCPA',f'{dcpa:.2f} NM')
c2.metric('TCPA',f'{tcpa/60:.1f} min')
c3.metric('Risk flag','HIGH' if risk else 'LOW')
c4.metric('Own heading',f'{st.session_state.heading:.0f}°')

left,right=st.columns([1.6,1])
with left:
    fig=go.Figure()
    # Radar-style background, relative distances in nautical miles.
    for radius in (1,2,3,4,5):
        theta=np.linspace(0,2*np.pi,160)
        fig.add_trace(go.Scatter(x=own[0]+radius*np.cos(theta),y=own[1]+radius*np.sin(theta),mode='lines',line=dict(color='rgba(88,170,191,0.20)',width=1,dash='dot'),hoverinfo='skip',showlegend=False))
    for angle in range(0,360,45):
        ang=np.deg2rad(angle)
        fig.add_trace(go.Scatter(x=[own[0],own[0]+5*np.sin(ang)],y=[own[1],own[1]+5*np.cos(ang)],mode='lines',line=dict(color='rgba(88,170,191,0.12)',width=1),hoverinfo='skip',showlegend=False))
    # Hull shapes rotate with the heading and represent the ship, not just a marker.
    def ship_shape(pos,hdg,color,label):
        hull=np.array([[0,.23],[-.095,.07],[-.095,-.18],[0,-.22],[.095,-.18],[.095,.07]])
        a=np.deg2rad(hdg)
        R=np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
        xy=hull@R.T+pos
        fig.add_trace(go.Scatter(x=list(xy[:,0])+[xy[0,0]],y=list(xy[:,1])+[xy[0,1]],fill='toself',mode='lines',line=dict(color=color,width=2),fillcolor=color,name=label,hovertemplate=f'{label}<br>Heading {hdg:.0f}°<extra></extra>'))
        fig.add_annotation(x=pos[0]+.22,y=pos[1]+.22,text=label,showarrow=False,font=dict(color=color,size=11))
    if len(st.session_state.history)>1:
        h=np.array(st.session_state.history)
        fig.add_trace(go.Scatter(x=h[:,0],y=h[:,1],mode='lines',line=dict(color='#58d7f5',width=2),name='Track history'))
    for name,p,v,color in [('Own projection',own,vo,'#59d8f5'),('Target projection',target,vt,'#ffac67')]:
        end=p+v*min(tcpa,1200)
        fig.add_trace(go.Scatter(x=[p[0],end[0]],y=[p[1],end[1]],mode='lines',line=dict(color=color,dash='dash',width=2),name=name))
    if mode!='Human Only':
        predicted=own+vel(own_speed,(st.session_state.heading+rec_delta)%360)*600
        fig.add_trace(go.Scatter(x=[own[0],predicted[0]],y=[own[1],predicted[1]],mode='lines',line=dict(color='#72ef9a',width=4),name='AI proposed heading'))
    if tcpa<1800:
        a=own+vo*tcpa;b=target+vt*tcpa
        fig.add_trace(go.Scatter(x=[a[0],b[0]],y=[a[1],b[1]],mode='lines+markers',line=dict(color='#ff6977',dash='dot',width=2),marker=dict(size=5),name='CPA separation'))
    ship_shape(own,st.session_state.heading,'#62dbf5','OWN SHIP')
    ship_shape(target,th,'#ffae70','TARGET A')
    fig.update_layout(title=dict(text='◉  LIVE TRAFFIC RADAR  ·  Synthetic scenario',font=dict(size=16,color='#bce7f3')),xaxis_title='East (NM)',yaxis_title='North (NM)',height=550,paper_bgcolor='#0a2332',plot_bgcolor='#102d3c',font=dict(color='#d3e9f2'),xaxis=dict(gridcolor='rgba(115,170,189,0.15)',zeroline=False),yaxis=dict(scaleanchor='x',scaleratio=1,gridcolor='rgba(115,170,189,0.15)',zeroline=False),legend=dict(orientation='h',y=-0.24,font=dict(size=10)),margin=dict(l=20,r=20,t=55,b=50))
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Blue: own ship · Orange: target · Green: AI proposal · Red: projected closest approach. Zoom and pan directly on the radar.')
with right:
    st.subheader('Decision support')
    if mode=='Human Only':
        st.info('AI advice hidden. Choose a manual course alteration.')
    else:
        st.write(f'**Geometric suggestion:** {rec_delta:+.0f}° course alteration')
        st.write(f'Predicted DCPA after alteration: **{rec_cpa:.2f} NM**')
        st.write(f'**Reason:** Candidate headings were ranked by projected closest approach; threshold = 0.50 NM. This is not a COLREG assessment.')
        st.write(f'**Uncertainty input:** ±{noise} m (display only; not propagated into the prediction).')
    manual=st.slider('Manual course alteration (degrees)',-60,60,15,5)
    if mode=='Human + AI':
        a,b,c=st.columns(3)
        action=''
        if a.button('Accept AI',use_container_width=True): action='Accepted AI';delta=rec_delta
        if b.button('Reject AI',use_container_width=True): action='Rejected AI';delta=0
        if c.button('Modify',use_container_width=True): action='Modified AI';delta=manual
    elif mode=='Human Only':
        action='Manual decision' if st.button('Apply manual action') else ''
        delta=manual
    else:
        action='AI automatic' if st.button('Apply AI action') else ''
        delta=rec_delta
    if action:
        st.session_state.heading=(st.session_state.heading+delta)%360
        st.session_state.log.append(dict(timestamp=datetime.now(timezone.utc).isoformat(),scenario=scenario,mode=mode,decision=action,delta_deg=delta,dcpa_before_nm=round(dcpa,3),tcpa_before_min=round(tcpa/60,2),sim_time_s=t))
        st.success(f'{action}: heading adjusted by {delta:+.0f}°')
    if st.button(f'Advance simulation +{step} s',type='primary'):
        st.session_state.own_pos=st.session_state.own_pos+vel(own_speed,st.session_state.heading)*step
        st.session_state.history.append(tuple(st.session_state.own_pos))
        st.session_state.tick+=step;st.rerun()

st.divider()
st.subheader('Experiment log')
if st.session_state.log:
    df=pd.DataFrame(st.session_state.log)
    st.dataframe(df,use_container_width=True)
    st.download_button('Download experiment CSV',df.to_csv(index=False).encode(),'experiment_log.csv','text/csv')
else: st.caption('Make a decision to populate the experiment log.')
st.warning('Research-only demonstration. Point-mass kinematics, a single target, instantaneous heading changes, no validated COLREG logic, no environmental forces, and no real-world navigation suitability. The uncertainty slider is illustrative only.')
