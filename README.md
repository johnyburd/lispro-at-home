
# Editing System
 I'm choosing HR because it is the simplest choice, and it worked for the PN1 -> PN2 transformation. I believe the low efficiency can be overcome with the nourseothricin selection marker.  Crispr or knocking out KU70 to force the yeast to choose HR over NHEJ are other possible avenues. 
##### References
 * [Genome Editing Systems Across Yeast Species](https://pmc.ncbi.nlm.nih.gov/articles/PMC7744358/)

# Loci

| Name | Notes                                                                                                                                                                                                                                                                                                     |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| YPS1 | - protease KO candidate<br>- yapsin 1 protease - likely to attack lispro as its being secreted<br>- Might be more effective in combination with PEP4<br>- Likely relevant regardless of the promoter used<br>- Yps1 may play a role in alpha factor cleaving, but it seems like KEX2 is the primary gene. |
| PEP4 | - protease KO candidate<br>- proteinase A, proteinase B, carboxypeptidase Y<br>- PEP4 gene secretes vacuolar proteases into the broth<br>- SMD1168 (pep4Δ) and SMD1163 (pep4Δ prb1Δ)<br>- possibly more relevant if we use the AOX1 promoter                                                              |
| AOX1 | "standard" locus for the AOX1 promoter                                                                                                                                                                                                                                                                    |
| PRB1 | ?                                                                                                                                                                                                                                                                                                         |

##### References
* [Disruption of YPS1 and PEP4 genes reduces proteolytic degradation of secreted HSA/PTH in Pichia pastoris GS115](https://academic.oup.com/jimb/article/40/6/589/5994886)
* [Handbook of Proteolytic Enzymes - Yapsin 1](https://www.sciencedirect.com/science/chapter/edited-volume/abs/pii/B9780120796113500410)
* [Yield improvement of heterologous peptides expressed in _yps1_-disrupted _Saccharomyces cerevisiae_ strains](https://www.sciencedirect.com/science/article/abs/pii/S0141022900001587)
* [Gleeson et al. 1998](https://www.researchgate.net/publication/13603766_Generation_of_Protease-Deficient_Strains_and_Their_Use_in_Heterologous_Protein_Expression)

# Homology Arms
1. Follow the 1st protocol [^MIMB1] to prep the gDNA. It looks like it will be suitable for the homology arms because the authors were able to PCR amplify a 4394 bp segment which is much larger than the planned homology arms.
2. Use synthesized primers to amplify homology arms targeting the genes in [[#Loci]] with the syntax referenced in [[#Assembly]].

##### References
[^MIMB1]: [Isolation of _Pichia pastoris_ Genomic DNA for Long-Read DNA Sequencing and PCR Applications](https://doi.org/10.1007/978-1-0716-4779-0_3)
##### Materials
* [Lumiprobe DNA Purification Columns](https://www.lumiprobe.com/p/nap-10-dna-purification-columns)


# CDS

## AA Sequence


this structure is mostly based on kjeldsen but currently it's lacking some major improvements around folding, secretion, and purification.

| Segment                       | Length | Sequence                                                           | Notes                                             |
| ----------------------------- | ------ | ------------------------------------------------------------------ | ------------------------------------------------- |
| α-factor pre (signal peptide) | 19     | `MRFPSIFTAVLFAASSALA`                                              | signal peptidase cuts in the ER                   |
| α-factor pro region           | 64     | `APVSTTTEDETAQIPVEAVIGYLDLEGDFDVAVLPFSNSTNNGLLFINTTIASIAAKEEGVSLD` |                                                   |
| Kex2 site                     | 2      | `KR`                                                               | Kex2 cleaves α-factor off in the Golgi            |
| B chain                       | 30     | `FVNQHLCGSHLVEALYLVCGERGFFYTKPT`                                   | Lispro swap from human insulin                    |
| Linker / conversion handle    | 3      | `AAK`                                                              | Trypsin cuts this out in-vitro. possibly optional |
| A chain                       | 21     | `GIVEQCCTSICSLYQLENYCN`                                            |                                                   |
|                               |        |                                                                    |                                                   |
![[Pasted image 20260924002629.png|865]]


##### References
* [[kjeldsen2000.pdf]]
* HL18 fusion [Functional expression of recombinant insulins in Saccharomyces cerevisiae](https://link.springer.com/content/pdf/10.1186/s12934-024-02571-2.pdf)
* [Molecular engineering of insulin for recombinant expression in yeast](https://www.sciencedirect.com/science/article/pii/S016777992300286X)

## Promoter

| Name  | Notes                                                                                                                          | References |
| ----- | ------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| AOX1p | - requires methanol which could be hard to work with or acquire<br>- commonly used (e.g. OpenInsulin) Biocon                   |            |
| GAPp  | - Constitutive promoter, can be tested in the shake flask<br>- Seems like it would be easier for testing, worse for production |            |
| GAL   | ?                                                                                                                              |            |

# Assembly
![447](https://experiment-uploads.s3.amazonaws.com/1244205/1roZSgScS0W34uWJMVW0_F1-OYC-Schema-EduKit.svg)

##### References
* https://experiment.com/u/HXePMQ

# Roadmap

1. Choose a protease [[#Loci|locus]] to knock out. Current choice: YPS1
2. Design primers to amplify the homology arms and add an overhang compatible with the OYC golden gate assembly syntax
	1. Order the HA primers
	2. extract dna from yeast
	3. run PCR
	4. gel or column purification to get the HA
	5. the purified arms can be frozen for later
3. Design & order primers that overlap the integration site to validate where the integration occurred.
4. Obtain the NAT s2-s3 part
	1. either by PCRing lox sites onto `BBF10K_000472` or by getting one synthesized
		1. not sure if this is possible... if it is we'd have to anneal inside of the BsaI sites and then add them back outside of the new lox sites
	2. Use lox66/71 sites, not loxP since that could have a chance of interacting with the existing lox scar
5. Order the codon-optimized CDS for lispro with overhang compatible with the OYC golden gate assembly syntax
	1. The current CDS in benchling likely has some problems
		1. the trypsin linker
		2. some extra bases after the overhang?
6. Golden Gate everything together
7. Transform into ecoli to make copies
8. linearize and transform into yeast
9. Select on [Nourseothricin](https://en.wikipedia.org/wiki/Nourseothricin) plates
10. See if we can detect any insulin
	1. ELISA or anti-insulin AB
11. Remove the NAT gene
	1. Build a episomal cre expression plasmid (`BBF10K_000207` ?)
		1. Select using Zeocin
	2. Optionally: try using electrophoresis to directly introduce cre instead
12. Testing and purification
