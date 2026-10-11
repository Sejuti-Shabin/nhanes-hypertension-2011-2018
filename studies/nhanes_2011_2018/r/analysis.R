# Reference estimation: full pooled survey design BEFORE domains; never ordinary GLM SE.
suppressPackageStartupMessages(library(survey));suppressPackageStartupMessages(library(foreign))
options(survey.lonely.psu='fail',survey.adjust.domain.lonely=FALSE)
args<-commandArgs(trailingOnly=TRUE);root<-if(length(args))normalizePath(args[1])else normalizePath('.')
out<-file.path(root,'outputs');rawdir<-file.path(root,'data/raw')
d<-read.csv(file.path(out,'design_frame.csv'),na.strings=c('','NA'),check.names=FALSE)
levels_list<-list(cycle=c('2011–2012','2013–2014','2015–2016','2017–2018'),sex=c('Female','Male'),race=c('White','Black','Mexican American','Other Hispanic','Asian','Other/multiracial'),education=c('College graduate','Some college/AA','High school/GED','Below high school'),race4=c('White','Black','Hispanic','Other'),age_group=c('18–24','25–34','35–44','45–54','55–64'),college=c('College graduate','Below college'),college_adult=c('College graduate','Below college'),income=c('75,000+','45,000–74,999','20,000–44,999','<20,000'),income_family=c('75,000+','45,000–74,999','20,000–44,999','<20,000'),smoking=c('Never','Former','Current'),pir_group=c('PIR >2','PIR >1–2','PIR ≤1'))
# Independent source reconstruction of all case, exposure, outcome and covariate variables.
vars<-list(DEMO=c('SEQN','RIDAGEYR','RIAGENDR','RIDRETH3','DMDEDUC2','DMDEDUC3','INDHHIN2','INDFMIN2','INDFMPIR','RIDSTATR','WTMEC2YR','SDMVSTRA','SDMVPSU','RIDEXPRG'),BPX=c('SEQN',paste0('BPXSY',1:4),paste0('BPXDI',1:4)),BPQ=c('SEQN','BPQ020','BPQ040A','BPQ050A'),HIQ=c('SEQN','HIQ011','HIQ210'),HUQ=c('SEQN','HUQ030'),BMX=c('SEQN','BMXBMI'),SMQ=c('SEQN','SMQ020','SMQ040'))
frames<-list()
for(s in c('G','H','I','J')) {
 components<-lapply(names(vars),function(comp) {
  x<-read.xport(file.path(rawdir,paste0(comp,'_',s,'.xpt')))
  stopifnot(!anyDuplicated(x$SEQN))
  for(v in names(x))if(is.numeric(x[[v]]))x[[v]][!is.na(x[[v]])&abs(x[[v]])<1e-50]<-0
  selected<-vars[[comp]]
  if(comp=='HUQ')selected<-c(selected,if(s=='G')'HUQ040'else'HUQ041')
  x<-x[,selected,drop=FALSE]
  names(x)[names(x) %in% c('HUQ040','HUQ041')]<-'place_type'
  x
 });names(components)<-names(vars)
 x<-components$DEMO
 for(comp in names(components)[-1])x<-merge(x,components[[comp]],by='SEQN',all.x=TRUE,sort=FALSE)
 x$suffix<-s;frames[[s]]<-x
}
r<-do.call(rbind,frames);r<-r[match(paste(d$suffix,d$SEQN),paste(r$suffix,r$SEQN)),]
stopifnot(all(r$SEQN==d$SEQN),all(r$suffix==d$suffix),all(r$RIDSTATR==2),all(r$WTMEC2YR>0))
r$cycle<-c(G='2011–2012',H='2013–2014',I='2015–2016',J='2017–2018')[r$suffix]
r$sbp<-rowMeans(r[,paste0('BPXSY',1:3)],na.rm=TRUE);r$dbp<-rowMeans(r[,paste0('BPXDI',1:3)],na.rm=TRUE)
r$sbp23<-rowMeans(r[,c('BPXSY2','BPXSY3')]);r$dbp23<-rowMeans(r[,c('BPXDI2','BPXDI3')])
r$sbp23_available<-rowMeans(r[,c('BPXSY2','BPXSY3')],na.rm=TRUE);r$dbp23_available<-rowMeans(r[,c('BPXDI2','BPXDI3')],na.rm=TRUE)
for(v in c('sbp','dbp','sbp23','dbp23','sbp23_available','dbp23_available'))r[[v]][is.nan(r[[v]])]<-NA
r$awareness<-c(1,0)[match(r$BPQ020,c(1,2))];r$unawareness<-1-r$awareness
r$medication<-c(1,0)[match(r$BPQ050A,c(1,2))]
# Current-medication status stays missing for skipped items as requested; no imputation.
phenotype<-function(sy,di,med,sth=130,dth=80) {
 measured<-ifelse(!is.na(sy)&!is.na(di),0,NA);measured[which(sy>=sth|di>=dth)]<-1
 ht<-rep(NA_real_,length(sy));ht[which(measured==1|med==1)]<-1;ht[which(measured==0&med==0)]<-0
 list(elevated=measured,hypertension=ht)
}
for(tag in c('130','140','23','23_available')) {
 sy<-if(tag=='23')r$sbp23 else if(tag=='23_available')r$sbp23_available else r$sbp
 di<-if(tag=='23')r$dbp23 else if(tag=='23_available')r$dbp23_available else r$dbp
 p<-phenotype(sy,di,r$medication,if(tag=='140')140 else 130,if(tag=='140')90 else 80)
 r[[paste0('elevated_',tag)]]<-p$elevated;r[[paste0('hypertension_',tag)]]<-p$hypertension
}
r$uninsured<-c(0,1)[match(r$HIQ011,c(1,2))];r$no_routine<-c(0,1,1)[match(r$HUQ030,1:3)];r$routine<-1-r$no_routine
r$no_any_place<-c(0,1,0)[match(r$HUQ030,1:3)]
r$no_routine_non_emergency_care<-rep(NA_real_,nrow(r))
r$no_routine_non_emergency_care[r$HUQ030 %in% 2]<-1
r$no_routine_non_emergency_care[r$HUQ030 %in% c(1,3)&r$place_type %in% 3]<-1
r$no_routine_non_emergency_care[r$HUQ030 %in% c(1,3)&r$place_type %in% c(1,2,4,5)]<-0
r$routine_non_emergency<-1-r$no_routine_non_emergency_care
r$sex<-c('Male','Female')[match(r$RIAGENDR,1:2)]
r$race<-c('Mexican American','Other Hispanic','White','Black','Asian','Other/multiracial')[match(r$RIDRETH3,c(1,2,3,4,6,7))]
r$race4<-c('Hispanic','Hispanic','White','Black','Other','Other')[match(r$RIDRETH3,c(1,2,3,4,6,7))]
r$education<-c('Below high school','Below high school','High school/GED','Some college/AA','College graduate')[match(r$DMDEDUC2,1:5)]
r$college_adult<-c('Below college','Below college','Below college','Below college','College graduate')[match(r$DMDEDUC2,1:5)]
r$college<-r$college_adult
r$college[which(r$RIDAGEYR>=18&r$RIDAGEYR<=19&(r$DMDEDUC3 %in% c(0:14,55,66)))]<-'Below college'
income<-function(x) {
 values<-rep(NA_character_,length(x));values[x %in% c(1:4,13)]<-'<20,000';values[x %in% 5:7]<-'20,000–44,999';values[x %in% 8:10]<-'45,000–74,999';values[x %in% c(14,15)]<-'75,000+';values
}
r$income<-income(r$INDHHIN2);r$income_family<-income(r$INDFMIN2)
r$pir<-ifelse(r$INDFMPIR>=0&r$INDFMPIR<=5,r$INDFMPIR,NA)
r$pir_group<-as.character(cut(r$pir,c(-.001,1,2,5),labels=c('PIR ≤1','PIR >1–2','PIR >2')))
r$age10<-(r$RIDAGEYR-40)/10;r$age10_sq<-r$age10^2
r$age_group<-as.character(cut(r$RIDAGEYR,c(17,24,34,44,54,64),labels=levels_list$age_group))
r$obese<-ifelse(!is.na(r$BMXBMI),as.numeric(r$BMXBMI>=30),NA)
r$smoking<-rep(NA_character_,nrow(r));r$smoking[r$SMQ020 %in% 2]<-'Never';r$smoking[r$SMQ020 %in% 1&r$SMQ040 %in% 3]<-'Former';r$smoking[r$SMQ020 %in% 1&r$SMQ040 %in% 1:2]<-'Current'
r$WTMEC8YR<-r$WTMEC2YR/4
checkvars<-c('sbp','dbp','sbp23','dbp23','sbp23_available','dbp23_available','awareness','unawareness','medication','uninsured','no_routine','routine','no_any_place','no_routine_non_emergency_care','routine_non_emergency','sex','race','race4','education','college','college_adult','income','income_family','pir','pir_group','age10','age10_sq','age_group','obese','smoking','WTMEC8YR',paste0('elevated_',c('130','140','23','23_available')),paste0('hypertension_',c('130','140','23','23_available')))
checks<-data.frame(variable=checkvars,passed=sapply(checkvars,function(v)isTRUE(all.equal(unname(r[[v]]),unname(d[[v]]),tolerance=1e-10))))
write.csv(checks,file.path(out,'r_raw_coding_validation.csv'),row.names=FALSE);stopifnot(all(checks$passed))
for(v in names(levels_list))d[[v]]<-factor(d[[v]],levels=levels_list[[v]])
full<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTMEC8YR,data=d,nest=TRUE)
fullj<-svydesign(ids=~psu_id,strata=~stratum_id,weights=~WTMEC2YR,data=d[d$suffix=='J',],nest=TRUE)

# Independent domain masks from raw variables, compared to every Python specification.
carevars<-c('unawareness','no_routine_non_emergency_care','age10','sex','race4','college','pir','obese','smoking')
insvars<-c('awareness','uninsured','age10','sex','race','education','pir')
care<-r$RIDAGEYR>=18&r$RIDAGEYR<=64&!is.na(r$sbp)&!is.na(r$dbp)&r$elevated_130==1
care[is.na(care)]<-FALSE
ins<-r$RIDAGEYR>=20&r$RIDAGEYR<=64&r$hypertension_130==1;ins[is.na(ins)]<-FALSE
carecommon<-care&complete.cases(r[,carevars]);inscommon<-ins&complete.cases(r[,insvars])
mask_for<-function(spec) {
 rule<-spec$rule;mask<-if(grepl('^care',rule))care else ins
 if(rule=='care_common')mask<-carecommon
 if(rule=='care_available')mask<-r$RIDAGEYR>=18&r$RIDAGEYR<=64&!is.na(r$sbp23_available)&!is.na(r$dbp23_available)&r$elevated_23_available==1
 if(rule=='care_strict23')mask<-r$RIDAGEYR>=18&r$RIDAGEYR<=64&!is.na(r$sbp23)&!is.na(r$dbp23)&r$elevated_23==1
 if(rule=='care_age20')mask<-mask&r$RIDAGEYR>=20
 if(rule=='care_exclude_ER')mask<-mask&!(r$place_type %in% 3)
 if(rule=='insurance_common')mask<-inscommon
 if(rule=='I3_measured')mask<-r$RIDAGEYR>=20&r$RIDAGEYR<=64&r$elevated_130==1
 if(rule=='I3_140')mask<-r$RIDAGEYR>=20&r$RIDAGEYR<=64&r$hypertension_140==1
 if(rule=='I3_readings23')mask<-r$RIDAGEYR>=20&r$RIDAGEYR<=64&r$hypertension_23_available==1
 if(rule %in% c('I3_measured23','I3_measured23_age18'))mask<-r$RIDAGEYR>=(if(rule=='I3_measured23')20 else 18)&r$RIDAGEYR<=64&r$elevated_23==1
 if(rule=='I3_bp_complete')mask<-mask&!is.na(r$sbp)&!is.na(r$dbp)
 if(rule=='I3_not_pregnant')mask<-mask&!(r$RIDEXPRG %in% 1)
 if(rule=='single_J')mask<-mask&r$suffix=='J'
 mask<-mask&complete.cases(r[,all.vars(as.formula(spec$formula)),drop=FALSE]);mask[is.na(mask)]<-FALSE
 stopifnot(all(mask==(d[[spec$domain_column]]==1)))
 mask
}
specs<-read.csv(file.path(out,'model_specifications.csv'),stringsAsFactors=FALSE)
regs<-list();covariances<-list();diags<-list();domainchecks<-list();fits<-list()
for(i in seq_len(nrow(specs))) {
 spec<-specs[i,];mask<-mask_for(spec)
 dd<-if(spec$scope=='single_J')subset(fullj,mask[d$suffix=='J']) else subset(full,mask)
 mod<-svyglm(as.formula(spec$formula),design=dd,family=if(spec$family=='logit')quasibinomial()else quasipoisson(),control=glm.control(epsilon=1e-14,maxit=200))
 if(!mod$converged||any(!is.finite(coef(mod))))stop('Unstable reference model')
 fits[[spec$model]]<-mod;b<-coef(mod);cv<-vcov(mod);se<-sqrt(diag(cv));rdf<-mod$df.residual;critical<-qt(.975,rdf)
 regs[[i]]<-data.frame(model=spec$model,family=spec$family,term=names(b),beta=b,se=se,ratio=exp(b),ci_low=exp(b-critical*se),ci_high=exp(b+critical*se),p=2*pt(abs(b/se),df=rdf,lower.tail=FALSE),n=sum(mask),events=sum(d[[spec$outcome]][mask]),design_df=degf(dd),residual_df=rdf,kind=spec$kind,row.names=NULL)
 cc<-expand.grid(term1=rownames(cv),term2=colnames(cv),stringsAsFactors=FALSE);cc$model<-spec$model;cc$covariance<-as.vector(cv);covariances[[i]]<-cc
 predictions<-as.numeric(fitted(mod));diags[[i]]<-data.frame(model=spec$model,n=sum(mask),rank=mod$rank,converged=mod$converged,min_prediction=min(predictions),max_prediction=max(predictions),predictions_above_one_n=sum(predictions>1),design_df=degf(dd),residual_df=rdf)
 domainchecks[[i]]<-data.frame(model=spec$model,n=sum(mask),raw_rebuilt_matches_python=TRUE)
}
reg<-do.call(rbind,regs)
write.csv(reg,file.path(out,'regression.csv'),row.names=FALSE)
write.csv(do.call(rbind,covariances),file.path(out,'r_covariance.csv'),row.names=FALSE)
write.csv(do.call(rbind,diags),file.path(out,'r_diagnostics.csv'),row.names=FALSE)
write.csv(do.call(rbind,domainchecks),file.path(out,'r_domain_validation.csv'),row.names=FALSE)
# Explicit reference calibration; same point estimates and SE, no result-driven choice.
calibrations<-lapply(c('residual','full_design','normal'),function(label) {
 z<-subset(reg,term %in% c('uninsured','no_routine_non_emergency_care','no_routine','no_any_place'));df<-if(label=='residual')z$residual_df else if(label=='full_design')z$design_df else Inf
 q<-qt(.975,df);z$reference<-label;z$inference_df<-df;z$ci_low<-exp(z$beta-q*z$se);z$ci_high<-exp(z$beta+q*z$se);z$p<-2*pt(abs(z$beta/z$se),df=df,lower.tail=FALSE);z
})
write.csv(do.call(rbind,calibrations),file.path(out,'inference_calibrations.csv'),row.names=FALSE)

# Descriptors and Table1 use variable-specific domains, bounded proportion intervals.
source(file.path(root,'r/reliability.R'))
estimate<-function(y,mask,binary=FALSE,design=full) {
 mask<-mask&!is.na(y);mask[is.na(mask)]<-FALSE
 dd<-design;dd$variables$y<-y;dd<-subset(dd,mask);n<-sum(mask)
 if(!n)stop('Empty requested descriptor')
 m<-svymean(~y,dd);p<-as.numeric(coef(m));se<-as.numeric(SE(m));df<-degf(dd);ci<-as.numeric(confint(m,df=df))
 flag<-'not a proportion';compflag<-'';neff<-NA_real_
 if(binary){k<-kg_interval(p,se,n,df);ci<-k$ci;neff<-k$effective_n;flag<-nchs_screen(p,n,neff,ci,df);compflag<-nchs_screen(1-p,n,neff,1-rev(ci),df)}
 data.frame(n=n,estimate=p,se=se,ci_low=ci[1],ci_high=ci[2],design_df=df,effective_n=neff,reliability=flag,complement_reliability=compflag)
}
requests<-read.csv(file.path(out,'python_descriptive.csv'),stringsAsFactors=FALSE)
rows<-list()
for(i in seq_len(nrow(requests))) {
 row<-requests[i,];mask<-if(row$analysis=='Calixte attempt')carecommon else if(row$analysis=='Calixte measured domain')care else ins&!is.na(d$awareness)&!is.na(d$uninsured)
 if(row$group=='Routine non-emergency place')mask<-mask&d$no_routine_non_emergency_care==0
 if(row$group=='No routine non-emergency place')mask<-mask&d$no_routine_non_emergency_care==1
 if(row$group=='Insured')mask<-mask&d$uninsured==0
 if(row$group=='Uninsured')mask<-mask&d$uninsured==1
 if(row$variable=='hypertension_130')mask<-d$RIDAGEYR>=20&d$RIDAGEYR<=64
 rows[[i]]<-cbind(row[,c('analysis','group','variable')],estimate(d[[row$variable]],mask,TRUE))
}
write.csv(do.call(rbind,rows),file.path(out,'descriptive.csv'),row.names=FALSE)
# Established grouped interface used as an additional descriptor check.
write.csv(svyby(~awareness,~uninsured,subset(full,domain_insurance_cases==1&!is.na(awareness)&!is.na(uninsured)),svymean,vartype=c('se','ci')),file.path(out,'r_svyby_insurance.csv'),row.names=FALSE)
requests<-read.csv(file.path(out,'python_table1.csv'),stringsAsFactors=FALSE)
tab<-list()
for(i in seq_len(nrow(requests))) {
 row<-requests[i,];mask<-if(row$analysis=='Calixte attempt')carecommon else ins&!is.na(d$awareness)&!is.na(d$uninsured)
 if(row$analysis=='Calixte attempt')mask<-mask&d$no_routine_non_emergency_care==as.numeric(row$group=='No routine non-emergency place') else mask<-mask&d$uninsured==as.numeric(row$group=='Uninsured')
 categorical<-row$variable %in% names(levels_list)
 y<-if(categorical)ifelse(is.na(d[[row$variable]]),NA,as.numeric(d[[row$variable]]==row$level)) else d[[row$variable]]
 tab[[i]]<-cbind(row[,c('analysis','group','variable','level','group_n','category_n')],estimate(y,mask,categorical||row$variable %in% c('unawareness','awareness')))
}
write.csv(do.call(rbind,tab),file.path(out,'table1.csv'),row.names=FALSE)

# Joint Taylor model-standardization uncertainty, then independent refitted JKn below.
mod<-fits[['I3']];keep<-inscommon;sub<-d[keep,];x<-model.matrix(mod);w<-sub$WTMEC8YR;y<-sub$awareness;p<-as.numeric(fitted(mod))
bread<-crossprod(x,x*as.numeric(w*p*(1-p)));score<-x*as.numeric(w*(y-p));lin<-score%*%solve(bread)
full_beta<-matrix(0,nrow(d),ncol(x));full_beta[keep,]<-lin
mus<-numeric(2);infs<-list()
for(k in 1:2){z<-sub;z$uninsured<-k-1;xn<-model.matrix(delete.response(terms(mod)),z,contrasts.arg=mod$contrasts);pred<-plogis(xn%*%coef(mod));mu<-sum(w*pred)/sum(w);grad<-colSums(xn*as.numeric(w*pred*(1-pred)))/sum(w);inf<-as.numeric(full_beta%*%grad);inf[keep]<-inf[keep]+w*(pred-mu)/sum(w);mus[k]<-mu;infs[[k]]<-inf}
mus[3]<-mus[2]-mus[1];infs[[3]]<-infs[[2]]-infs[[1]]
marginal<-list()
for(k in 1:3){dd<-full;dd$variables$lin<-infs[[k]]/d$WTMEC8YR;se<-as.numeric(SE(svytotal(~lin,dd)));q<-qt(.975,mod$df.residual);ci<-mus[k]+c(-1,1)*q*se;if(k<=2)ci<-plogis(qlogis(mus[k])+c(-1,1)*q*se/(mus[k]*(1-mus[k])));marginal[[k]]<-data.frame(estimand=c('Insured','Uninsured','Uninsured minus insured')[k],estimate=mus[k],se=se,ci_low=ci[1],ci_high=ci[2],design_df=degf(full),inference_df=mod$df.residual,n=sum(keep))}
write.csv(do.call(rbind,marginal),file.path(out,'marginal_probabilities.csv'),row.names=FALSE)
saveRDS(list(primary_insurance=fits[['I3']],full_design_df=degf(full)),file.path(out,'r_models.rds'))
capture.output(sessionInfo(),file=file.path(out,'R_sessionInfo.txt'))
cat('R reference completed:',nrow(reg),'coefficient rows; pooled design df',degf(full),'\n')
receipt<-c('r/analysis.R','r/reliability.R','outputs/design_frame.csv','outputs/model_specifications.csv',paste0('outputs/',c('regression.csv','r_covariance.csv','r_raw_coding_validation.csv','r_domain_validation.csv','descriptive.csv','table1.csv','marginal_probabilities.csv')))
write.csv(data.frame(path=receipt,md5=unname(tools::md5sum(file.path(root,receipt)))),file.path(out,'r_reference_receipt.csv'),row.names=FALSE)
# Native CDC masked strata are unique across these four cycles; test equivalent namespaces.
namespace_design<-svydesign(ids=~psu_id,strata=~stratum_id,weights=~WTMEC8YR,data=d,nest=TRUE)
namespace_fit<-svyglm(awareness~uninsured+age10+sex+race+education+pir,subset(namespace_design,inscommon),family=quasibinomial(),control=glm.control(epsilon=1e-14,maxit=200))
stopifnot(isTRUE(all.equal(coef(namespace_fit),coef(fits[['I3']]),tolerance=1e-10)),isTRUE(all.equal(vcov(namespace_fit),vcov(fits[['I3']]),tolerance=1e-10)))
write.csv(data.frame(native_design_df=degf(full),namespace_design_df=degf(namespace_design),coefficients_equal=TRUE,covariance_equal=TRUE),file.path(out,'r_design_namespace_validation.csv'),row.names=FALSE)
