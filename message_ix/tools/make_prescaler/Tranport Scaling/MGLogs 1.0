$ontext
                                         == Model for Gas Logistics Systems (MGLogs) ==
=============================== An MILP Model for Optimal Planning of Small-scale LNG Logistics Systems ===============================
=      (c) Yoga Wienda Pratama, Widodo Wahyu Purwanto                                                                                 =
=          Department of Chemical Engineering, Faculty of Engineering Universitas Indonesia - Depok, Jawa Barat INDONESIA 16424       =
=          Sustainable Energy Systems & Policy Research Cluster (SESP - UI) Universitas Indonesia - Depok, Jawa Barat INDONESIA 16424 =
=======================================================================================================================================
$offtext

$set Data 'MGLogs_Input0'
*Read data from Excel and store in GDX file.
$call gdxxrw %Data%.xlsx skipempty=0 trace=2 index=Specs!A1
$gdxin %Data%.gdx
*$gdxin MGLogs_Input.gdx


Sets
         i       locations
         s       storages
         c       vessels
         r       route slots
         l       frequency       / 1*100 /;
$load i,s,c,r

Alias    (i,j,k) ;

Parameters
         di(i,i)    distance between locations
         d(i)       demand of LNG at location i in m3 of LNG
         capexc(c)  capital expenditures of vessels (USD per unit)
         capexs(s)  capital expenditures of storage and FSRU (USD per unit)
         capexns(s) capital expenditures of non storage facility and onshore interface for FSRU (USD per m3 per year)
         fec(c)     fuel economy of vessel (MMBTU per nautical mile)
         ucc(c)     unit capacity of vessel (m3)
         ucs(s)     unit capacity of storage or FSRU (m3)
         vc(c)      velocity of vessel (kn)
         lurc(c)    loading unloading rate of vessel (m3 per hr)
         btc(c)     berthing time of vessels
         c_lp(j)    liquefaction plant production capacity (m3 per year)
         nTr(l)     number of frequency in binary linearization
         pg(i)      price of LNG  ($ p MMBTU) ;

$load di,d,capexc,capexs,capexns,fec,ucc,ucs,vc,lurc,btc,c_lp, pg
nTr(l) = ord(l) ;

SCALARS  fomc     fixed operating and maintenance carrier
         fomr     fixed operating and maintenance costs of regas
         cgr      cost of gas regasification ($ p m3)
         svr      coefficient for storage volume reserve
         hvc      heels volume of carrier
         cbogc    coefficient of BOG for vessels (LNG transported per day)
         pd       price of diessel fuel ($ p MMBTU)
         crfc     cost recovery factor
         crfr     cost recovery factor
         ghv      m3 to mmbtu
         m        any large number for number of storage
         scur_up  upper bound for storage capacity for vessel unloading
         scsor_up upper bound for storage capacity for send out
         sclr_up  upper bound for storage capacity for vessel loading
         itc      Idle time of vessel (hr)
         ;

$load fomc,fomr,cgr,svr,hvc,cbogc,pd,crfc,crfr,ghv,m,scur_up,scsor_up,sclr_up,itc

VARIABLES
*Objective Function
         TASC Total annual systems cost US$
         CoG  Cost in gas from liquefaction terminal
         CoC  Cost in vessels
         CoR  Cost in receiving terminal
         ;

POSITIVE VARIABLES
*Vessels
         Lv(i,r,c,j)     Volume of LNG from liquefaction terminal i loaded to vessel (m3 LNG)
         Tv(i,r,c,j,k)   Volume of LNG from liquefaction terminal i transported by vessel from terminals j to k (m3 LNG)
         Uv(i,r,c,j)     Volume of LNG from liquefaction terminal i unloaded from vessel to terminal j (m3 LNG)
         Rv(i,r,c,j)     Volume of LNG from liquefaction terminal i remains in vessel after unloading in terminal j (m3 LNG)
         Bogv(i,r,c,j,k) Volume of LNG from liquefaction terminal i boiled off during travel from j to k
         Dec(i,r,c,j,k)  Diessel fuel consumption from j to k (MMBTU)
         Hv(i)           Heels' volume of carriers (m3 of LNG)

*Receiving Terminals
         Scr(j)           Storage capacity of receiving terminal (m3 LNG)
         Socr(j)          Send-out capacity of receiving terminal (m3 LNG per year)
         Scsor(l,i,r,c,k) Storage capacity for send out (m3 LNG)
         Sclr(l,i,r,c,j)  Storage capacity for vessels loading from receiving terminal (m3 LNG)
         Scur(l,i,r,c,k)  Storage capacity for unloading
         Sorr(i,r,c,k)    Send-out rate of receiving terminal (m3 LNG per year)

         ;
BINARY VARIABLES
         Sb(s,j)         Storage type selection
         Rb(l,i,r,c,j,k)   Route selection
         ;

INTEGER VARIABLES
         Nc(i,r,c)
         Nsr(s,j)
         Tr(i,r,c,j,k)
         ;

EQUATIONS
         EQ1
         EQ2
         EQ3
         EQ4
         EQ5(j)
         EQ6(r,k)
         EQ7(r,j)
         EQ8(k)
         EQ9(j)
         EQ10(l,i,r,c,j,k)
         EQ11(l,i,r,c,k)
         EQ12(i,r,c,j,k)
         EQ13(i,r,c,k)
         EQ14(i,r,c,j)
         EQ15(i,r,c,j,k)
         EQ16(i,r,c,j)
         EQ17(j)
         EQ18(j)
         EQ19(i,r,c,j,k)
         EQ20(i,r,c,j,k)
         EQ21(i,r,c,j,k)
         EQ22(i,r,c)
         EQ23(i)
         EQ24(j)
         EQ25(k)
         EQ26(k)
**       EQ27(i,r,c,j,k)
         EQ27a(i,r,c,k)
         EQ27b(l,i,r,c,k)
**       EQ28(i,r,c,j,k)
         EQ28a(i,r,c,j,k)
         EQ28b(l,i,r,c,k)
**       EQ29(i,r,c,j,k)
         EQ29a(i,r,c,j)
         EQ29b(l,i,r,c,j)
         EQ30(s,j)
         EQ31(s,j)
         EQ32(j)
         EQ33(j)
         EQ34(i,r,c,j,k)
         ;

*Statement of Equations
*Objective Function
         EQ1.. TASC =E= CoG + CoR + CoC ;
         EQ2.. CoG =E= sum[i, pg(i) * ghv * (sum[(r,c,j), Lv(i,r,c,j)$(ord(i) < 3)] - sum[(r,c,j,k), Bogv(i,r,c,j,k)] - Hv(i))] ;
         EQ3.. CoC =E= sum[(i,r,c), Nc(i,r,c) * (capexc(c) * (crfc + fomc))] + sum[(i,r,c,j,k), Dec(i,r,c,j,k) * pd + Bogv(i,r,c,j,k) * ghv * pg(i)] ;
         EQ4.. CoR =E= (sum[(s,i)$(ord(s) = 1), Nsr(s,i) * capexs(s) + Socr(i) * capexns(s)] + sum[(s,i)$(ord(s) > 1), Nsr(s,i) * capexs(s) + Socr(i) * capexns(s)]) * (crfr + fomr) + sum[i, d(i) * cgr] ;

*Constraints
*Supply Demand Balance
         EQ5(j).. sum[(i,r,c), Sorr(i,r,c,j)] =E= d(j) ;
*Vehicle flow formulation
*--------untuk hub, untuk masing-masing rs, boleh didatangi dan ditinggal masing-masing sekali
         EQ6(r,k).. sum[(l,i,c,j)$(ord(i) = ord(k)), Rb(l,i,r,c,j,k)] =L= 1 ;
         EQ7(r,j).. sum[(l,i,c,k)$(ord(i) = ord(j)), Rb(l,i,r,c,j,k)] =L= 1 ;
*--------kalau bukan hub, hanya boleh didatangi dan ditinggal oleh 1 rute untuk semua slot
         EQ8(k).. sum[(l,i,r,c,j)$(ord(i) <> ord(k)), Rb(l,i,r,c,j,k)] =L= 1 ;
         EQ9(j).. sum[(l,i,r,c,k)$(ord(i) <> ord(j)), Rb(l,i,r,c,j,k)] =L= 1 ;
         EQ10(l,i,r,c,j,k)$(ord(j) = ord(k)).. Rb(l,i,r,c,j,k) =E= 0 ;
         EQ11(l,i,r,c,k)..  sum[j, Rb(l,i,r,c,j,k)] =E= sum[j, Rb(l,i,r,c,k,j)] ;

*LNG balance in Vessels
         EQ12(i,r,c,j,k).. Tr(i,r,c,j,k) =E= sum[l, Rb(l,i,r,c,j,k) * nTR(l)] ;
         EQ13(i,r,c,k).. sum[j, Tv(i,r,c,j,k)] =E= Uv(i,r,c,k) +Rv(i,r,c,k) ;
         EQ14(i,r,c,j).. sum[k, Tv(i,r,c,j,k)] =E= Rv(i,r,c,j) + Lv(i,r,c,j) - sum[k, Bogv(i,r,c,j,k)] ;
         EQ15(i,r,c,j,k).. Bogv(i,r,c,j,k) =E= cbogc * (di(j,k) / [vc(c) * 24]) * (Tv(i,r,c,j,k) + Bogv(i,r,c,j,k)) ;
         EQ16(i,r,c,j)$(ord(i) <> ord(j)).. Lv(i,r,c,j) =E= 0 ;
         EQ17(j).. sum[(i,r,c), Lv(i,r,c,j)$(ord(j) < 3)] =L= c_lp(j) ;
         EQ18(j).. sum[(i,r,c), Lv(i,r,c,j)$(ord(j) > 2)] =L= sum[(i,r,c), Uv(i,r,c,j)] - sum[(i,r,c), Sorr(i,r,c,j)] ;
         EQ19(i,r,c,j,k).. Tv(i,r,c,j,k) + Bogv(i,r,c,j,k) =L= Tr(i,r,c,j,k) * ucc(c) ;
         EQ20(i,r,c,j,k).. Tv(i,r,c,j,k) =G= Tr(i,r,c,j,k) * hvc * ucc(c) ;
         EQ21(i,r,c,j,k)$(ord(i) = ord(k)).. Tv(i,r,c,j,k) =E= Tr(i,r,c,j,k) * hvc * ucc(c) ;
         EQ22(i,r,c).. Nc(i,r,c) * (8766 - itc) =G= sum[(j,k), Tr(i,r,c,j,k) * ([di(j,k)/vc(c)] + btc(c))] + sum[k, Uv(i,r,c,k)/lurc(c)] + sum[j, Lv(i,r,c,j)/lurc(c)] ;

*Heels of Ship
         EQ23(i).. Hv(i) =E= sum[(r,c), hvc * Nc(i,r,c) * ucc(c)] ;

*Storage size constraints
         EQ24(j).. Scr(j) =E= sum[s, Nsr(s,j) * ucs(s)] ;
         EQ25(k).. Scr(k) =G= sum[(l,i,r,c), Scur(l,i,r,c,k)] ;
         EQ26(k).. Scr(k) =G= sum[(l,i,r,c), Scsor(l,i,r,c,k)] + sum[(l,i,r,c), Sclr(l,i,r,c,k)] ;

**       Do not remove
**       EQ27(i,r,c,j,k)$(ord(i) <> ord(k)).. Scur(i,r,c,j,k) * Tr(i,r,c,j,k) =E= svr * Uv(i,r,c,k) ;
         EQ27a(i,r,c,k)$(ord(i) <> ord(k)).. svr * Uv(i,r,c,k) =L= sum[l, nTR(l) *  Scur(l,i,r,c,k)] ;
         EQ27b(l,i,r,c,k)$(ord(i) <> ord(k)).. Scur(l,i,r,c,k) =L= scur_up * sum[j, Rb(l,i,r,c,j,k)] ;
**       Do not remove
**       EQ28(i,r,c,j,k)$(ord(i) <> ord(k)).. Scsor(i,r,c,j,k) * Tr(i,r,c,j,k) =E= svr * Sorr(i,r,c,k) ;
         EQ28a(i,r,c,j,k)$(ord(i) <> ord(k)).. svr * Sorr(i,r,c,k) =L= sum[l, nTR(l) *  Scsor(l,i,r,c,k)] ;
         EQ28b(l,i,r,c,k)$(ord(i) <> ord(k)).. Scsor(l,i,r,c,k) =L= scsor_up * sum[j, Rb(l,i,r,c,j,k)] ;
**       Do not remove
**       EQ29(i,r,c,j,k)$(ord(i) = ord(j) and ord(i) > 2).. Sclr(i,r,c,j,k) * Tr(i,r,c,j,k) =E= svr * Lv(i,r,c,j) ;
         EQ29a(i,r,c,j)$(ord(i) > 2).. svr * Lv(i,r,c,j) =L= sum[l, nTR(l) *  Sclr(l,i,r,c,j)] ;
         EQ29b(l,i,r,c,j)$(ord(i) > 2).. Sclr(l,i,r,c,j) =L= sclr_up * sum[k, Rb(l,i,r,c,j,k)] ;
         EQ30(s,j)$(ord(s) = 1).. Nsr(s,j) =L= Sb(s,j) * m ;
         EQ31(s,j)$(ord(s) > 1).. Nsr(s,j) =L= Sb(s,j) ;
         EQ32(j).. sum[s, Sb(s,j)] =L= 1 ;
         EQ33(j).. Socr(j) =E= sum[(i,r,c), Sorr(i,r,c,j)] ;

*Fuel Consumption for Shipping
         EQ34(i,r,c,j,k).. Dec(i,r,c,j,k) + (BOGV(i,r,c,j,k) * ghv) =E= fec(c) * Tr(i,r,c,j,k) * di(j,k) ;

         Nc.up(i,r,c) = 3 ;
         Nsr.up(s,j) = 10 ;
         Tr.up(i,r,c,j,k) = card(l) ;



MODEL MGLogs       / all /
OPTION mip = CPLEX ;
OPTION reslim = 864000;
OPTION threads = 12;
OPTION optcr = 0.03 ;
MGLogs.nodlim = 10000000;
SOLVE MGLogs using MIP minimize TASC;


$set datatype Output
$set outputname (SESP-UI)
Execute_Unload "MGLogs_%datatype%_%outputname%.gdx";


$ontext

$offtext
