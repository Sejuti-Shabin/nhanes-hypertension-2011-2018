# Nonlinear JKn checks and supplemental PIR response weighting; full design before domains.
suppressPackageStartupMessages(library(survey));options(survey.lonely.psu='fail')
args<-commandArgs(trailingOnly=TRUE);root<-if(length(args))normalizePath(args[1])else normalizePath('.')
out<-file.path(root,'outputs');d<-read.csv(file.path(out,'design_frame.csv'),na.strings=c('','NA'),check.names=FALSE)
levels_list<-list(cycle=c('2011–2012','2013–2014','2015–2016','2017–2018'),sex=c('Female','Male'),race=c('White','Black','Mexican American','Other Hispanic','Asian','Other/multiracial'),education=c('College graduate','Some college/AA','High school/GED','Below high school'),race4=c('White','Black','Hispanic','Other'),college=c('College graduate','Below college'),smoking=c('Never','Former','Current'))
for(v in names(levels_list))d[[v]]<-factor(d[[v]],levels=levels_list[[v]])
full<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTMEC8YR,nest=TRUE,data=d)
repfull<-as.svrepdesign(full,type='JKn',mse=TRUE)
formula_i<-awareness ~ uninsured + age10 + sex + race + education + pir
formula_a<-unawareness ~ no_routine_non_emergency_care + age10 + sex + race4 + college + pir + obese + smoking
fit_score<-function(data,w,formula,family=quasibinomial()) {
 data$.analysis_weight<-w/mean(w[w>0]);x<-model.matrix(formula,data)
 if(qr(x[w>0,,drop=FALSE])$rank!=ncol(x))stop('Rank deficient replicate')
 fit<-glm(formula,data=data,weights=.analysis_weight,family=family,control=glm.control(epsilon=1e-12,maxit=200))
 if(!fit$converged||any(!is.finite(coef(fit))))stop('Unstable replicate')
 fit
}
standardize<-function(fit,data,w) {
 p<-sapply(0:1,function(k){z<-data;z$uninsured<-k;as.numeric(predict(fit,z,type='response'))})
 mu<-colSums(p*w)/sum(w)
 c(uninsured_beta=unname(coef(fit)['uninsured']),Insured=mu[1],Uninsured=mu[2],Difference=mu[2]-mu[1])
}
message('Refitting insurance model/standardization under JKn')
rep_i<-subset(repfull,domain_insurance_complete==1)
i_result<-withReplicates(rep_i,function(w,data)standardize(fit_score(data,w,formula_i),data,w),return.replicates=TRUE)
reg<-read.csv(file.path(out,'regression.csv'));marginal<-read.csv(file.path(out,'marginal_probabilities.csv'))
refse<-c(reg$se[reg$model=='I3'&reg$term=='uninsured'],marginal$se)
checks<-data.frame(analysis='Insurance',estimand=names(coef(i_result)),estimate=as.numeric(coef(i_result)),jackknife_se=as.numeric(SE(i_result)),taylor_se=refse,ratio=as.numeric(SE(i_result))/refse,replicates=nrow(i_result$replicates))
message('Refitting approximate Study A under JKn')
a_result<-withReplicates(subset(repfull,domain_care_complete==1),function(w,data)unname(coef(fit_score(data,w,formula_a,quasipoisson()))['no_routine_non_emergency_care']),return.replicates=TRUE)
a_se<-reg$se[reg$model=='A4'&reg$term=='no_routine_non_emergency_care']
checks<-rbind(checks,data.frame(analysis='Approximate replication',estimand='no_non_emergency_beta',estimate=as.numeric(coef(a_result)),jackknife_se=as.numeric(SE(a_result)),taylor_se=a_se,ratio=as.numeric(SE(a_result))/a_se,replicates=length(a_result$replicates)))
checks$flag<-ifelse(checks$ratio<.7|checks$ratio>1.3,'Review departure','Within diagnostic range; not exact equivalence')
write.csv(checks,file.path(out,'jackknife_validation.csv'),row.names=FALSE)
write.csv(as.data.frame(i_result$replicates),file.path(out,'insurance_jackknife_replicates.csv'),row.names=FALSE)
write.csv(as.data.frame(a_result$replicates),file.path(out,'care_jackknife_replicates.csv'),row.names=FALSE)

# Supplemental MAR-dependent item-response weighting, not a demonstrated bias correction.
base<-d$domain_insurance_cases==1&complete.cases(d[,c('awareness','uninsured','age10','sex','race','education')])
d$pir_observed<-as.numeric(!is.na(d$pir));d$bp_missing<-as.numeric(is.na(d$sbp)|is.na(d$dbp));d$log_exam_weight<-log(d$WTMEC8YR)
d$sbp_aux<-ifelse(is.na(d$sbp),weighted.mean(d$sbp[base],d$WTMEC8YR[base],na.rm=TRUE),d$sbp)/10
d$dbp_aux<-ifelse(is.na(d$dbp),weighted.mean(d$dbp[base],d$WTMEC8YR[base],na.rm=TRUE),d$dbp)/10
response_formula<-pir_observed ~ uninsured * awareness + age10 + I(age10^2) + sex + race + education + sbp_aux + dbp_aux + bp_missing + log_exam_weight + cycle
response_theta<-function(w,data,details=FALSE) {
 ms<-weighted.mean(data$sbp,w,na.rm=TRUE);md<-weighted.mean(data$dbp,w,na.rm=TRUE)
 data$sbp_aux<-ifelse(is.na(data$sbp),ms,data$sbp)/10;data$dbp_aux<-ifelse(is.na(data$dbp),md,data$dbp)/10
 response<-fit_score(data,w,response_formula);p<-as.numeric(predict(response,type='response'))
 if(any(!is.finite(p))||any(p<=0)||any(p>=1))stop('Response positivity / separation failure')
 observed<-data$pir_observed==1;adjusted<-w[observed]/p[observed]
 result<-standardize(fit_score(data[observed,],adjusted,formula_i),data[observed,],adjusted)
 if(details)return(list(result=result,p=p,observed=observed,adjusted=adjusted,rank=response$rank))
 result
}
message('Refitting response and outcome models under JKn; PIR MAR sensitivity')
full_response<-svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTMEC8YR,nest=TRUE,data=d)
response_rep<-subset(as.svrepdesign(full_response,type='JKn',mse=TRUE),base)
response_result<-withReplicates(response_rep,response_theta,return.replicates=TRUE)
point<-response_theta(d$WTMEC8YR[base],d[base,],TRUE)
vals<-as.numeric(coef(response_result));se<-as.numeric(SE(response_result));rdf<-reg$residual_df[reg$model=='I3'&reg$term=='uninsured'];q<-qt(.975,rdf)
rows<-data.frame(estimand=c('Uninsured OR','Insured','Uninsured','Difference'),estimate=vals,se=se,ci_low=vals-q*se,ci_high=vals+q*se,inference_df=rdf,target_n=sum(base),observed_n=sum(base&!is.na(d$pir)))
rows$estimate[1]<-exp(vals[1]);rows$ci_low[1]<-exp(vals[1]-q*se[1]);rows$ci_high[1]<-exp(vals[1]+q*se[1])
for(k in 2:3){ci<-plogis(qlogis(vals[k])+c(-1,1)*q*se[k]/(vals[k]*(1-vals[k])));rows$ci_low[k]<-ci[1];rows$ci_high[k]<-ci[2]}
write.csv(rows,file.path(out,'pir_response_weighting.csv'),row.names=FALSE)
write.csv(as.data.frame(response_result$replicates),file.path(out,'pir_response_replicates.csv'),row.names=FALSE)
write.csv(data.frame(target_n=sum(base),missing_other_covariates_excluded=sum(d$domain_insurance_cases==1&!is.na(d$awareness)&!is.na(d$uninsured))-sum(base),missing_PIR_n=sum(base&is.na(d$pir)),min_response_probability=min(point$p),max_response_probability=max(point$p),max_inverse_response_factor=max(1/point$p),kish_weight_effective_n=sum(point$adjusted)^2/sum(point$adjusted^2),response_rank=point$rank,replicates=nrow(response_result$replicates)),file.path(out,'pir_response_summary.csv'),row.names=FALSE)
writeLines(paste(deparse(response_formula),collapse=' '),file.path(out,'pir_response_model.txt'))
stopifnot(all(is.finite(as.matrix(response_result$replicates))),all(is.finite(checks$jackknife_se)))
cat('R JKn and PIR response sensitivity complete; replicates:',nrow(response_result$replicates),'\n')
receipt<-c('r/robustness.R','outputs/design_frame.csv','outputs/regression.csv',paste0('outputs/',c('jackknife_validation.csv','pir_response_weighting.csv','pir_response_summary.csv','pir_response_replicates.csv')))
write.csv(data.frame(path=receipt,md5=unname(tools::md5sum(file.path(root,receipt)))),file.path(out,'r_robustness_receipt.csv'),row.names=FALSE)
