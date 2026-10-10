/*****************************************************************
Program:    table_ae_summary.sas
Purpose:    Table 14.3.1 Overview of Treatment-Emergent Adverse Events
            by System Organ Class and Preferred Term
Input:      adae (adverse event analysis dataset), adsl
Output:     RTF table via ODS, n (%) by SOC/PT x treatment arm
Status:     Authored SAS program, NOT executed in this environment --
            see src/generate_tlfs.py for the executed Python mirror.
******************************************************************/

ods rtf file="&outpath./t_14_3_1_ae_summary.rtf" style=journal bodytitle;

proc sql;
    create table ae_counts as
    select a.trt01pn, a.aesoc, a.aedecod, count(distinct a.usubjid) as n_subj
    from adae a
    where a.trtemfl = "Y"
    group by a.trt01pn, a.aesoc, a.aedecod;
quit;

proc sql noprint;
    select count(*) into :bign1 from adsl where trt01pn = 1;
    select count(*) into :bign2 from adsl where trt01pn = 2;
    select count(*) into :bign3 from adsl where trt01pn = 3;
quit;

title1 "Table 14.3.1";
title2 "Overview of Treatment-Emergent Adverse Events";
title3 "by System Organ Class and Preferred Term, Safety Population";

proc report data=ae_counts nowd headline headskip split="~";
    column aesoc aedecod trt01pn, n_subj;
    define aesoc / group "System Organ Class";
    define aedecod / group "Preferred Term";
    define trt01pn / across "Treatment Arm";
    define n_subj / analysis sum "n";
run;

footnote1 "n = number of subjects reporting at least one treatment-emergent AE in the category.";
footnote2 "Program: table_ae_summary.sas  Output: t_14_3_1_ae_summary.rtf";

ods rtf close;
