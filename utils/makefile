all: susyhit micromegas

# SUSYHIT
SUSYHIT = ./susyhit
susyhit:
	[ -d $(SUSYHIT) ] || (wget https://www.itp.kit.edu/~maggie/SUSY-HIT/susyhit.tar.gz && mkdir $(SUSYHIT) && tar -xf susyhit.tar.gz -C $(SUSYHIT) && rm susyhit.tar.gz)	
	[ -f $(SUSYHIT)/run ] || (cd $(SUSYHIT) && make)
	(cp -r for_LDM_MSSM.susyhit $(SUSYHIT)/suspect2_lha.in)

# MicrOMEGAs
MicrOMEGAs = ./micromegas
micromegas:
	[ -d $(MicrOMEGAs) ] || (wget https://lapth.cnrs.fr/micromegas/downloadarea/code/micromegas_5.0.6.tgz && tar xzf micromegas_5.0.6.tgz && mv micromegas_5.0.6 $(MicrOMEGAs) && rm micromegas_5.0.6.tgz)
	(cp -r for_LDM_MSSM.micromegas $(MicrOMEGAs)/MSSM/main.c) 
	[ -f $(MicrOMEGAs)/lib/micromegas.a ] || (cd $(MicrOMEGAs) && make) 
	[ -f $(MicrOMEGAs)/MSSM/main ] || (cd $(MicrOMEGAs)/MSSM && make main=main.c)
    
.PHONY: clean
clean: 
	rm -rf $(SUSYHIT) $(MicrOMEGAs)
