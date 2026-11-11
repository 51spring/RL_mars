import unittest
from mars_env.multiyear_n import cumulative_terms
from mars_env.integrated_n import run_tables


class MultiyearNTests(unittest.TestCase):
    def test_prior_external_ledgers_survive_crop_counter_reset(self):
        finals={1:dict(seed_n=.2,cum_n=.1),3:dict(seed_n=.3,cum_n=.2)}
        current=dict(canopy_n=.5,rootn=.5,population=1,seed_n=.3,cum_n=.2,root_sen_n=.1)
        states={(3,1983100):(current,.2)};exports={1:4,3:6}
        initial=cumulative_terms(3,1983029,states,finals,exports)
        active=cumulative_terms(3,1983100,states,finals,exports)
        final=cumulative_terms(4,1984029,states,finals,exports)
        for values,expected in ((initial,(2,1,4,0)),(active,(5,3,4,10)),(final,(5,3,10,0))):
            for key,value in zip(('seed','damage','harvest','plant'),expected):
                self.assertAlmostEqual(values[key],value)

    def test_four_run_tables_require_explicit_domain_and_keep_initialization_rows(self):
        text='\n'.join(f'*RUN {r}\n@YEAR DOY DAS\n 1982 {r:03} 0\n 1982 {r+1:03} 1' for r in range(1,5))
        with self.assertRaises(ValueError):run_tables(text)
        rows=run_tables(text,expected_runs=(1,2,3,4))
        self.assertEqual(sum(len(r) for r in rows.values()),8)
        with self.assertRaises(ValueError):run_tables(text.replace('*RUN 4','*RUN 3'),expected_runs=(1,2,3,4))


if __name__=='__main__':unittest.main()
