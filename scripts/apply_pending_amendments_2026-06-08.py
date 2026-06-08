#!/usr/bin/env python3
"""Apply session-law-verified text to the 13 pending constitutional amendments.

Source-of-truth: the enacted session-law text in ~/refs/nd/sess (clean text
layers), transcribed in data/const_amend_session_law_extraction_2026-06-08.md.

10 structurally-clean amendments (whole-provision add/amend/repeal) are finalized
(status:pending dropped). 3 structurally-complex amendments (LXXVIII, XCVI amend
subsections of amend. art. LIV; LXXXI repeals one paragraph of §25) get their
now-verified verbatim text + high confidence but REMAIN pending until the full
enclosing provision is assembled (the ingest does whole-provision replacement).

Idempotent: re-running re-writes the same fields.
"""
import json
from pathlib import Path

JSON = Path("/Users/jerod/code/ndcourts-mcp/data/constitution_amendments.json")
SL = "https://www.legis.nd.gov/assembly/sessionlaws"

# ---- verbatim operative text (leading provision labels stripped; paragraphs \n\n) ----
S167 = ("The Legislative Assembly shall provide by general law for organizing new "
"counties, locating county seats thereof temporarily, and changing the county lines; "
"but no new county shall be organized, nor shall any organized county be so reduced "
"as to include an area of less than twenty-four congressional townships, and "
"containing a population of less than five thousand bona fide inhabitants. And in the "
"organization of new counties and in changing the lines of organized counties and "
"boundaries of congressional townships the natural boundaries shall be observed as "
"nearly as may be.\n\n"
"The Legislative Assembly shall also provide by general law for the consolidation of "
"counties, and for their dissolution, but no counties shall be consolidated without a "
"fifty-five per cent vote of those voting on the question in each county affected, and "
"no county shall be dissolved without a fifty-five per cent vote of the electors of "
"such county voting on such question.")

S170 = ("The Legislative Assembly shall provide by law for optional forms of government "
"for counties, which forms shall be, in addition to that form provided by Sections 172 "
"and 173 of the Constitution, and which forms shall specify the number, functions and "
"manner of selection of county officers, but no such optional form of government shall "
"become operative in any county until submitted to the electors thereof at a special "
"election or a general election, and approved by fifty-five per cent of those voting "
"thereon. The manner of exercising the powers herein granted shall be by general laws, "
"but such laws shall provide that the initiative for the submission of the question of "
"the adoption of one of the optional forms of county government may be had either by a "
"vote of not less than two-thirds of the county legislative body or upon petition of "
"electors of the county equal to at least fifteen per centum of the total number of "
"voters of the county who voted for Governor at the last general election. Among the "
"optional forms of county government to be provided by the Legislative Assembly under "
"this provision, at least one form shall provide for a county manager.")

S172 = ("Until one of the optional forms of county government provided by the Legislative "
"Assembly under Section 170 of the Constitution, as amended, be adopted by any county, "
"the fiscal affairs of said county shall be transacted by a board of county "
"commissioners. Said board shall consist of not less than three and not more than five "
"members whose terms of office shall be prescribed by law. Said board shall hold "
"sessions for the transaction of county business, as shall be provided by law.")

S173_LV = ("At the first general election after the adoption of this amendment, and every "
"two years thereafter, there shall be elected in each county organized under the "
"provisions of Section 172 of the Constitution, a register of deeds, county auditor, "
"treasurer, sheriff, state's attorney, county judge and a clerk of the district court, "
"who shall be electors in the county in which they are elected and who shall hold "
"office until their successors are elected and qualified; provided in counties having "
"fifteen thousand population or less, the county judge shall also be clerk of the "
"district court; provided further that in counties having a population of 6,000 or "
"less, the register of deeds shall also be clerk of the district court and county "
"judge. The sheriff and treasurer of any county shall not hold their respective "
"offices for more than four years in succession.")

S82 = ("There shall be chosen by the qualified electors of the state at the times and "
"places of choosing members of the legislative assembly, a secretary of state, "
"auditor, treasurer, superintendent of public instruction, commissioner of insurance, "
"three public service commissioners, an attorney general, a commissioner of "
"agriculture and labor, and a tax commissioner, who shall have attained the age of "
"twenty-five years and shall have the qualifications of state electors. They shall "
"severally hold their offices at the seat of government for the term of two years and "
"until their successors are elected and duly qualified; but no person shall be eligible "
"for the office of treasurer for more than two consecutive terms; provided, however, "
"the tax commissioner shall hold his office for the term of four years and until his "
"successor is elected and duly qualified; and provided, further, that the public "
"service commissioners shall severally hold their offices for the term of six years and "
"until their successors are elected and duly qualified.\n\n"
"The tax commissioner shall be elected on a no-party ballot and he shall be nominated "
"and elected in the manner now provided for the nomination and election of the "
"superintendent of public instruction. The first election of a tax commissioner shall "
"not occur until the year 1940.\n\n"
"At the general election in 1940 there shall be chosen two public service "
"commissioners to fill the two terms expiring on the first Monday in January, 1941. "
"The candidate at said election receiving the highest number of votes shall be elected "
"for a term of six years, and the candidate receiving the next highest number of votes "
"shall be elected for a term of four years. Thereafter there shall be chosen one such "
"public service commissioner every two years.\n\n"
"The board of railroad commissioners shall hereafter be known as the public service "
"commission and the members of the board of railroad commissioners as public service "
"commissioners and the powers and duties now or hereafter granted to and conferred "
"upon the board of railroad commissioners are hereby transferred to the public service "
"commission.")

S158 = ("No original grant school or institutional land shall be sold for less than the "
"fair market value thereof, and in no case for less than ten dollars ($10.00) per "
"acre, provided that when lands have been sold on contract and the contract has been "
"cancelled, such lands may be resold without reappraisement by the board of appraisal. "
"The purchaser shall pay twenty (20) per cent of the purchase price at the time the "
"contract is executed; thereafter annual payments shall be made of not less than six "
"(6) per cent of the original purchase price. An amount equal to not less than three "
"(3) per cent per annum of the unpaid principal shall be credited to interest and the "
"balance shall be applied as payment on principal as credit on purchase price. The "
"purchaser may pay all or any installment or installments not yet due to any interest "
"paying date. If the purchaser so desires, he may pay the entire balance due on his "
"contract with interest to date of payment at any time and he will then be entitled to "
"proper conveyance.\n\n"
"All sales shall be held at the county seat of the county in which the land to be sold "
"is situated, and shall be at public auction and to the highest bidder, and notice of "
"such sale shall be published once each week for a period of three weeks prior to the "
"day of sale in a legal newspaper published nearest the land and in the newspaper "
"designated for the publication of the official proceedings and legal notices within "
"the county in which said land is situated.\n\n"
"No grant or patent for such lands shall issue until payment is made for the same; "
"provided that the land contracted to be sold by the State shall be subject to taxation "
"from the date of the contract. In case the taxes assessed against any of said lands "
"for any year remain unpaid until the first Monday in October of the following year, "
"the contract of sale for such land shall, if the Board of University and School Lands "
"so determine, by it, be declared null and void. No contract of sale heretofore made "
"under the provisions of said Section 158 of the Constitution as then providing shall "
"be affected by this amendment, except prepayment of principal may be made as herein "
"provided.\n\n"
"Any of said lands that may be required for townsite purposes, school house sites, "
"church sites, cemetery sites, sites for other educational or charitable institutions, "
"public parks, air plane landing fields, fair grounds, public highways, railroad "
"right-of-way, or other railroad uses and purposes, reservoirs for the storage of "
"water for irrigation, irrigation canals, and ditches, drainage ditches, or for any of "
"the purposes for which private lands may be taken under the right of eminent domain "
"under the Constitution and Laws of this state, may be sold under the provisions of "
"this Article, and shall be paid for in full at the time of sale, or at any time "
"thereafter as herein provided. Any of said lands and any other lands controlled by "
"the Board of University and School Lands, may, with the approval of said Board, be "
"exchanged for lands of the United States, the State of North Dakota or any county or "
"municipality thereof as the Legislature may provide, and the lands so acquired shall "
"be subject to the trust to which the lands exchanged therefor were subject, and the "
"State shall reserve all mineral and water power rights in lands so transferred.\n\n"
"When any of said lands have been heretofore or may be hereafter sold on contract, and "
"the purchaser or his heirs or assigns is unable to pay in full for the land purchased "
"within twenty years after the date of purchase and such contract is in default and "
"subject to being declared null and void as by law provided, the Board of University "
"and School Lands may, after declaring such contract null and void, resell the land "
"described in such contract to such purchaser, his heirs or assigns, for the amount of "
"the unpaid principal, together with interest thereon reckoned to the date of such "
"resale at the rate of not less than three (3%) per cent, but in no case shall the "
"resale price be more than the original sale price; such contract of resale shall be "
"upon the terms herein provided, provided this section shall be deemed self-executing "
"insofar as the provisions for resale herein made are concerned.")

S_LIX = ("The legislative assembly of the state of North Dakota is hereby authorized and "
"empowered to provide by legislation for the issuance, sale, and delivery of the bonds "
"of the state of North Dakota in the principal amount of not to exceed $27,000,000.00, "
"the proceeds thereof to be used in the payment of adjusted compensation to North "
"Dakota veterans of World War II on the basis of term of service, and under such terms "
"and conditions as the legislative assembly may prescribe.")

S_LX = ("Section 1.) Upon the adoption of this amendment to the constitution of the state "
"of North Dakota there shall be annually levied by the state of North Dakota one mill "
"upon all of the taxable property within the state of North Dakota which, when "
"collected, shall be covered into the state treasury of the state of North Dakota and "
"placed to the credit of the North Dakota State Medical Center at the University of "
"North Dakota; said fund shall be expended as the legislature shall direct for the "
"development and maintenance necessary to the efficient operation of the said North "
"Dakota State Medical Center.\n\n"
"Section 2.) This amendment shall be self-executing, but legislation may be enacted to "
"facilitate its operation.")

S162 = ("The moneys of the permanent school fund and other educational funds shall be "
"invested only in bonds of school corporations or of counties, or of townships, or of "
"municipalities within the state, bonds issued for the construction of drains under "
"authority of law within the state, bonds of the United States, bonds of the state of "
"North Dakota, or on first mortgages on farm lands in this state to the extent such "
"mortgages are guaranteed or insured by the United States or any instrumentality "
"thereof, or if not so guaranteed or insured, not exceeding in amount one-half of the "
"actual value of any subdivision on which the same may be loaned such value to be "
"determined by the board of appraisal of school lands.")

S173_LXII = ("At the first general election after the adoption of this amendment, and "
"every two years thereafter, there shall be elected in each county, organized under "
"the provisions of section 172 of the constitution of the state of North Dakota, a "
"register of deeds, county auditor, treasurer, sheriff, state's attorney, county judge "
"and a clerk of the district court, who shall be electors in the county in which they "
"are elected and who shall hold office until their successors are elected and "
"qualified; provided in counties having fifteen thousand population or less, the county "
"judge shall also be clerk of the district court; provided further that in counties "
"having a population of six thousand or less, the register of deeds shall also be clerk "
"of the district court and county judge. The treasurer of any county shall not hold his "
"or her respective office for more than four years in succession. The legislative "
"assembly shall enact appropriate legislation to make this amendment effective at their "
"first session after its adoption.")

S138 = ("No corporation shall issue stock or bonds except for money, labor done, or money "
"or property actually received; and all fictitious increase of stock or indebtedness "
"shall be void. The stock and indebtedness of corporations shall not be increased "
"except in pursuance of general law, nor without the consent of the persons holding the "
"larger amount in value of the stock first obtained.")

S_LVI = ("Revenue from gasoline and other motor fuel excise and license taxation, motor "
"vehicle registration and license taxes, after deduction of cost of administration and "
"collection authorized by legislative appropriation only, and statutory refunds, shall "
"be appropriated and used solely for construction, reconstruction, repair and "
"maintenance of public highways, and the payment of obligations incurred in the "
"construction, reconstruction, repair and maintenance of public highways.")

S_LXXIII = ("1. Revenue from gasoline and other motor fuel excise and license taxation, "
"motor vehicle registration and license taxes, except revenue from aviation gasoline "
"and unclaimed aviation motor fuel refunds and other aviation motor fuel excise and "
"license taxation used by aircraft, after deduction of cost of administration and "
"collection authorized by legislative appropriation only, and statutory refunds, shall "
"be appropriated and used solely for construction, reconstruction, repair and "
"maintenance of public highways, and the payment of obligations incurred in the "
"construction, reconstruction, repair and maintenance of public highways.")

# structurally-complex (text verified; stays pending)
S_LXXVIII = ("6. (d) It shall be the duty of the heads of the several state institutions "
"hereinbefore mentioned, to submit the budget requests for the biennial appropriations "
"for said institutions to said state board of higher education; and said state board of "
"higher education shall consider said budgets and shall revise the same as in its "
"judgment shall be for the best interests of the educational system of the state; and "
"thereafter the state board of higher education shall prepare and present to the state "
"budget board and to the legislature a single unified budget covering the needs of all "
"the institutions under its control. \"Said budget shall be prepared and presented by "
"the board of administration until the state board of higher education organizes as "
"provided in section 6 (a).\" The appropriations for all of said institutions shall be "
"contained in one legislative measure. The budgets and appropriation measures for the "
"agricultural experiment stations and their substations and the extension division of "
"the North Dakota state university of agriculture and applied science may be separate "
"from those of state educational institutions.")

S_LXXXI_REPEALED = ("All measures submitted to the electors shall be published by the "
"state as follows: \"The secretary of state shall cause to be printed and mailed to "
"each elector a publicity pamphlet, containing a copy of each measure together with its "
"ballot title, to be submitted at any election. Any citizen, or the officers of any "
"organization, may submit to the secretary of state for publication in such pamphlet, "
"arguments concerning any measure therein, upon first subscribing their names and "
"addresses thereto and paying the fee therefor, which, until otherwise fixed by the "
"legislature, shall be the sum of two hundred dollars per page.\"")

S_XCVI_2 = ("2. (a) The State Board of Higher Education shall consist of seven members, "
"all of whom shall be qualified electors and taxpayers of the State, and who shall have "
"resided in this State for not less than five years immediately preceding their "
"appointment, to be appointed by the Governor, by and with the consent of the Senate, "
"from a list of names selected as hereinafter provided.\n\n"
"There shall not be on said board more than one graduate of any one of the institutions "
"under the jurisdiction of the State Board of Higher Education at any one time. No "
"person employed by any institution under the control of the board shall serve as a "
"member of the board, nor shall any employee of any such institution be eligible for "
"membership on the State Board of Higher Education for a period of two years following "
"the termination of his employment.\n\n"
"On or before the first day of February, 1939, the Governor shall nominate from a list "
"of three names for each position, selected by the unanimous action of the President of "
"the North Dakota Educational Association, the Chief Justice of the Supreme Court, and "
"the Superintendent of Public Instruction, and, with the consent of a majority of the "
"members-elect of the Senate, shall appoint from such list as such State Board of "
"Higher Education seven members, whose terms shall commence on the first day of July, "
"1939, one of which terms shall expire on the thirtieth day of June, 1940, and one on "
"the thirtieth day of June in each of the years 1941, 1942, 1943, 1944, 1945, and 1946. "
"The term of office of members appointed to fill vacancies at the expiration of said "
"terms shall be for seven years, and in the case of vacancies otherwise arising, "
"appointments shall be made only for the balance of the term of the members whose "
"places are to be filled.\n\n"
"(b) In the event any nomination made by the Governor is not consented to and confirmed "
"by the Senate as hereinbefore provided, the Governor shall again nominate a candidate "
"for such office, selected from a new list, prepared in the manner hereinbefore "
"provided, which nomination shall be submitted to the Senate for confirmation, and said "
"proceedings shall be continued until such appointments have been confirmed by the "
"Senate, or the session of the legislature shall have adjourned.\n\n"
"(c) When any term expires or a vacancy occurs when the legislature is not in session, "
"the Governor may appoint from a list selected as hereinbefore provided, a member who "
"shall serve until the opening of the next session of the legislature, at which time "
"his appointment shall be certified to the Senate for confirmation, as above provided; "
"and if the appointment be not confirmed by the thirtieth legislative day of such "
"session, his office shall be deemed vacant and the Governor shall nominate from a list "
"selected as hereinbefore provided, another candidate for such office and the same "
"proceedings shall be followed as are above set forth; provided further, that when the "
"legislature shall be in session at any time within six months prior to the date of the "
"expiration of the term of any member, the Governor shall nominate his successor from a "
"list selected as above set forth, within the first thirty days of such session, and "
"upon confirmation by the Senate such successor shall take office at the expiration of "
"the term of the incumbent. No person who has been nominated and whose nomination the "
"Senate has failed to confirm shall be eligible for an interim appointment.")

S_XCVI_4 = ("4. Each appointive member of the State Board of Higher Education shall "
"receive such compensation as may be determined by the Legislative Assembly for the "
"time actually spent devoted to the duties of his office, and, in addition, shall "
"receive his necessary expenses in the same manner and amounts as other state officials "
"for attending meetings and performing other functions of his office.")

# ---- per-amendment updates ----
# fields: election_date, effective_date, type, changes[], authority, source_urls,
#         sources_verified, confidence, finalize(bool — drop status:pending)
U = {
 "LV": dict(election="1940-06-25", eff="1940-07-25", typ="amend_section", finalize=True,
   changes=[
     {"target":"N.D. Const. § 167","heading":"Organization, consolidation, and dissolution of counties","text":S167},
     {"target":"N.D. Const. § 170","heading":"Optional forms of county government; county manager","text":S170},
     {"target":"N.D. Const. § 171","heading":"Township-board system of county government (repealed)","text":"","action":"repeal"},
     {"target":"N.D. Const. § 172","heading":"Board of county commissioners until optional form adopted","text":S172},
     {"target":"N.D. Const. § 173","heading":"Election of county officers under Section 172","text":S173_LV},
   ],
   authority="Article 55, County Government (submitted by Legislature); approved June 25, 1940, 67,804 to 64,519.",
   urls=[f"{SL}/1941/sl1941.pdf"],
   sv=["~/refs/nd/sess/sl1941.pdf pp. 587-588 (Constitutional Amendments — Approved, Article 55; clean text layer)"]),

 "LVI": dict(election="1940-06-25", eff="1940-07-25", typ="new_article", finalize=True,
   changes=[{"target":"N.D. Const. amend. art. LVI","heading":"Gasoline Motor Fuel Act — dedication of highway-user revenue","text":S_LVI}],
   authority="Article 56, Gasoline Motor Fuel Act (submitted by Initiative Petition); approved June 25, 1940, 91,149 to 49,324.",
   urls=[f"{SL}/1941/sl1941.pdf"],
   sv=["~/refs/nd/sess/sl1941.pdf p. 589 (Article 56; clean text layer). Recovered — previously 'TEXT NOT FOUND'."]),

 "LVII": dict(election="1940-06-25", eff="1940-07-25", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. § 82","heading":"Board of Railroad Commissioners renamed Public Service Commission","text":S82}],
   authority="Article 57, Transfer Power of Railroad Commission to Public Service Commission (submitted by Initiative Petition); approved June 25, 1940, 67,294 to 57,239.",
   urls=[f"{SL}/1941/sl1941.pdf"],
   sv=["~/refs/nd/sess/sl1941.pdf pp. 589-590 (Article 57; clean text layer)"]),

 "LVIII": dict(election="1944-06-27", eff="1944-07-27", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. § 158","heading":"Sale of school and public lands","text":S158}],
   authority="Article 58, Sale of School and Public Lands; approved June 27, 1944. Amends §158 of Art. 9 as previously amended by Articles 13 and 50.",
   urls=[f"{SL}/1945/sl1945.pdf", f"{SL}/1943/sl1943.pdf"],
   sv=["~/refs/nd/sess/sl1945.pdf pp. 492-493 (Article 58, Approved; OCR-dirty)",
       "~/refs/nd/sess/sl1943.pdf p. 182 (proposed concurrent resolution; clean — used to reconcile dirty approved scan)"]),

 "LIX": dict(election="1948-06-29", eff="1948-07-29", typ="new_article", finalize=True,
   changes=[{"target":"N.D. Const. amend. art. LIX","heading":"Bond issue — World War II adjusted compensation","text":S_LIX}],
   authority="Article 59, Bond Issue — World War II Adjusted Compensation (Ch. 123, S.L. 1947); approved June 29, 1948, 126,573 to 55,377.",
   urls=[f"{SL}/1949/sl1949.pdf"],
   sv=["~/refs/nd/sess/sl1949.pdf p. 510 (Article 59). CORRECTED subject: WWII veterans' adjusted compensation, not 'state building program.'"]),

 "LX": dict(election="1948-11-02", eff="1948-12-02", typ="new_article", finalize=True,
   changes=[{"target":"N.D. Const. amend. art. LX","heading":"State Medical Center — one-mill tax levy","text":S_LX}],
   authority="Article 60, State Medical Center — One-Mill Tax Levy (Ch. 119, S.L. 1947); approved November 2, 1948, 108,133 to 86,262.",
   urls=[f"{SL}/1949/sl1949.pdf"],
   sv=["~/refs/nd/sess/sl1949.pdf p. 511 (Article 60). CORRECTED subject: State Medical Center at UND, not generic 'state building.'"]),

 "LXI": dict(election="1952-06-24", eff="1952-07-24", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. § 162","heading":"Investment of moneys of the permanent school and educational funds","text":S162}],
   authority="Article 61, Investment of Moneys of the Permanent School Funds and Other Educational Funds (Ch. 347, S.L. 1951); approved June 24, 1952, 99,187 to 49,778.",
   urls=[f"{SL}/1953/sl1953.pdf"],
   sv=["~/refs/nd/sess/1953_sl/sl1953.pdf p. 589 (Article 61; clean). CORRECTED: §162 school-fund investment (record previously had no changes)."]),

 "LXII": dict(election="1952-06-24", eff="1952-07-24", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. § 173","heading":"Election of county officers; treasurer four-year limit","text":S173_LXII}],
   authority="Article 62, County Officers (Ch. 346, S.L. 1951); approved June 24, 1952, 100,197 to 59,694.",
   urls=[f"{SL}/1953/sl1953.pdf"],
   sv=["~/refs/nd/sess/1953_sl/sl1953.pdf pp. 589-590 (Article 62; clean). CORRECTED: §173 county officers (removes sheriff from the four-year-succession limit); prior heading 'school funds' belonged to LXI."]),

 "LXIV": dict(election="1954-06-29", eff="1954-07-29", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. § 138","heading":"Corporate issuance of stock and bonds","text":S138}],
   authority="Article 64, §138 (Corporate Stock and Bonds); approved June 29, 1954, 66,234 to 65,802. Removes the 60-day-notice requirement.",
   urls=[f"{SL}/1955/sl1955.pdf"],
   sv=["~/refs/nd/sess/1955_sl/sl1955.pdf p. 637 (Article 64; clean)"]),

 "LXXIII": dict(election="1960-06-28", eff="1960-07-28", typ="amend_section", finalize=True,
   changes=[{"target":"N.D. Const. amend. art. LVI","heading":"Article 56 re-enacted — aviation fuel taxes excluded from highway revenue","text":S_LXXIII}],
   authority="Re-enactment of Article 56 (aviation fuel taxes); approved June 28, 1960, 83,604 to 80,352.",
   urls=[f"{SL}/1961/pdf/CMA.pdf", f"{SL}/1959/pdf/CAP.pdf"],
   sv=["~/refs/nd/sess/1961_sl/CMA.pdf (Constitutional Measures, Approved; clean)",
       "~/refs/nd/sess/1959_sl/CAP.pdf (proposed SCR; clean, identical operative text)"]),

 # ---- structurally complex: verify text, bump confidence, STAY pending ----
 "LXXVIII": dict(election="1964-06-30", eff="1964-07-30", typ="amend_section", finalize=False,
   changes=[{"target":"N.D. Const. art. LIV, subsection 6(d)","heading":"Separation of budgets — subdivision (d) of subsection 6 of Article 54","text":S_LXXVIII}],
   authority="Subdivision (d) of subsection 6 of Article 54; approved June 30, 1964, 61,721 to 46,333.",
   urls=[f"{SL}/1965/pdf/CMA.pdf", f"{SL}/1963/pdf/CAP.pdf"],
   sv=["~/refs/nd/sess/1963_sl/CAP.pdf (proposed; clean)","~/refs/nd/sess/1965_sl/CMA.pdf (approved; clean)"],
   pending_reason="Text verified (high confidence). STRUCTURAL: amends only subdivision (d) of subsection 6 of amend. art. LIV, which is stored as a single provision; needs full art-LIV text spliced before whole-provision apply."),

 "LXXXI": dict(election="1964-11-03", eff="1964-12-03", typ="repeal", finalize=False,
   changes=[{"target":"N.D. Const. § 25","heading":"Publicity pamphlet — repeal of the tenth paragraph of §25","text":S_LXXXI_REPEALED}],
   authority="Repeal of the tenth paragraph of §25 (publicity pamphlet); approved November 3, 1964, 125,117 to 96,283.",
   urls=[f"{SL}/1965/pdf/CMA.pdf", f"{SL}/1963/pdf/CAP.pdf"],
   sv=["~/refs/nd/sess/1965_sl/CMA.pdf (approved; clean)","~/refs/nd/sess/1963_sl/CAP.pdf (proposed; clean)"],
   pending_reason="Text verified (high confidence). STRUCTURAL: PARTIAL repeal (only the tenth paragraph of §25); ingest 'repeal' would tombstone all of §25. Also: §25 already shows status='repealed' in the base — investigate before applying. Needs full §25 text minus the tenth paragraph."),

 "XCVI": dict(election="1976-11-02", eff="1976-12-02", typ="amend_section", finalize=False,
   changes=[
     {"target":"N.D. Const. art. LIV, subsection 2","heading":"Board of Higher Education — qualifications (subsection 2 of Article 54)","text":S_XCVI_2},
     {"target":"N.D. Const. art. LIV, subsection 4","heading":"Board of Higher Education — compensation (subsection 4 of Article 54)","text":S_XCVI_4},
   ],
   authority="SCR 4027, Ch. 612 S.L. 1975; Constitutional Amendments Approved Ch. 597; approved November 2, 1976, 136,720 to 99,080.",
   urls=[f"{SL}/1977/pdf/CAA.pdf"],
   sv=["~/refs/nd/sess/1977_sl/CAA.pdf pp. 1375-1376 (Ch. 597; clean)"],
   pending_reason="Text verified (high confidence). STRUCTURAL: amends subsections 2 and 4 of amend. art. LIV (stored as a single provision); needs full art-LIV text spliced before whole-provision apply."),
}

doc = json.loads(JSON.read_text())
recs = {r["number"]: r for r in doc["amendments"]}
applied, upgraded = [], []
for num, u in U.items():
    r = recs[num]
    r["election_date"] = u["election"]
    r["effective_date"] = u["eff"]
    r["type"] = u["typ"]
    r["changes"] = u["changes"]
    r["authority"] = u["authority"]
    r["source_urls"] = u["urls"]
    r["sources_verified"] = u["sv"]
    r["confidence"] = "high"
    r.pop("variants", None)
    if u["finalize"]:
        r.pop("status", None)
        r.pop("pending_reason", None)
        applied.append(num)
    else:
        r["status"] = "pending"
        r["pending_reason"] = u["pending_reason"]
        upgraded.append(num)

JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("FINALIZED (status:pending dropped):", ", ".join(applied))
print("UPGRADED (verified text, still pending):", ", ".join(upgraded))
still = [r["number"] for r in doc["amendments"] if r.get("status") == "pending"]
print("Total still pending:", len(still), "->", ", ".join(still))
