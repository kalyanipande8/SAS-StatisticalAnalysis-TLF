/*****************************************************************
Program:    table_demographics.sas
Purpose:    Table 14.1.1 Demographic and Baseline Characteristics
Input:      adsl (subject-level analysis dataset)
Output:     RTF table via ODS, one row per characteristic x treatment arm
Status:     Authored SAS program, NOT executed in this environment
            (no SAS license available) -- see src/generate_tlfs.py for
            an executed Python mirror of this exact table logic, used to
            validate the specification against simulated trial data.
******************************************************************/

ods rtf file="&outpath./t_14_1_1_demographics.rtf" style=journal bodytitle;

proc format;
    value trtfmt 1 = "Treatment A"  2 = "Treatment B"  3 = "Placebo";
run;

proc sql noprint;
    select count(*) into :n1 from adsl where trt01pn = 1;
    select count(*) into :n2 from adsl where trt01pn = 2;
    select count(*) into :n3 from adsl where trt01pn = 3;
quit;

title1 "Table 14.1.1";
title2 "Demographic and Baseline Characteristics";
title3 "Safety Population";

proc report data=adsl nowd headline headskip split="~";
    column trt01pn,(age sexn racen) n mean std median min max;
    define trt01pn / across format=trtfmt. "Treatment Arm~(N=&n1./&n2./&n3.)";
    define age / analysis mean std median min max "Age (years)";
    define sexn / analysis n "Sex";
    define racen / analysis n "Race";
run;

footnote1 "Age summarized as mean (SD), median, min-max.";
footnote2 "Program: table_demographics.sas  Output: t_14_1_1_demographics.rtf";

ods rtf close;
