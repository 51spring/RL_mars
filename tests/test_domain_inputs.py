import unittest
from mars_env.domain_inputs import soil_profile,diagnostic_soil_input,verify_effective_layers

SOIL='''*IB00000004 example
@ SLB SLMH SLLL SDUL SSAT
 5 -99 .1 .3 .4
 30 -99 .15 .35 .45
*OTHER next
'''
FILEX='''*FIELDS
@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME
 1 UFGA0002 UFGA       -99     0 DR000     0     0 00000 -99    180  IBMZ910014 Field section
*INITIAL CONDITIONS
@C  ICBL  SH2O  SNH4  SNO3
 1     5  .086    .5    .1
 1   180  .258    .5    .1
! preserved note
*PLANTING DETAILS
'''


class DomainInputTests(unittest.TestCase):
    def test_native_subdivision_allowed_but_wrong_soil_and_crossing_refused(self):
        p=soil_profile(SOIL,'IB00000004')
        rows=[dict(top=0,bottom=5,SLLL=.1,SDUL=.3,SSAT=.4,SH2O=.2),
              dict(top=5,bottom=15,SLLL=.15,SDUL=.35,SSAT=.45,SH2O=.25),
              dict(top=15,bottom=30,SLLL=.15,SDUL=.35,SSAT=.45,SH2O=.25)]
        self.assertTrue(verify_effective_layers(p,rows))
        with self.assertRaises(ValueError):verify_effective_layers(p,[dict(rows[0],bottom=15),rows[2]])
        with self.assertRaises(ValueError):verify_effective_layers(p,[dict(rows[0],SDUL=.31),*rows[1:]])
        with self.assertRaises(ValueError):verify_effective_layers(p,rows[:-1])
        tie={'layers':[dict(SLB=5,SLLL=.025,SDUL=.096,SSAT=.345)]}
        for printed in (.060,.061):
            self.assertTrue(verify_effective_layers(tie,[dict(top=0,bottom=5,SLLL=.025,
                SDUL=.096,SSAT=.345,SH2O=printed)]))

    def test_exact_profile_and_water_between_ll_and_dul(self):
        profile=soil_profile(SOIL,'IB00000004')
        self.assertEqual(len(profile['layers']),2)
        result=diagnostic_soil_input(FILEX,profile)
        self.assertIn('IB00000004',result);self.assertNotIn('IBMZ910014',result)
        rows=result.split('@C  ICBL  SH2O  SNH4  SNO3\n')[1].split('!')[0].splitlines()
        self.assertEqual([float(r.split()[2]) for r in rows],[.2,.25])
        self.assertIn('! preserved note',result)

    def test_missing_duplicate_and_nonphysical_profiles_refused(self):
        for source,identifier in ((SOIL,'missing'),(SOIL+SOIL,'IB00000004'),
                (SOIL.replace('.1 .3 .4','.4 .3 .4'),'IB00000004'),
                (SOIL.replace('30 -99','5 -99'),'IB00000004')):
            with self.assertRaises(ValueError):soil_profile(source,identifier)

    def test_invalid_initial_water_and_missing_filex_layer_header_refused(self):
        p=soil_profile(SOIL,'IB00000004')
        for fraction in (-.1,1.1,float('nan'),True):
            with self.assertRaises(ValueError):diagnostic_soil_input(FILEX,p,water_fraction=fraction)
        with self.assertRaises(ValueError):diagnostic_soil_input(FILEX.replace('@C  ICBL','@C  WRONG'),p)


if __name__=='__main__':unittest.main()
