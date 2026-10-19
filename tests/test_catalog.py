import copy, importlib.util, pathlib, unittest
p=pathlib.Path(__file__).parents[1]/'tools'/'validate_catalog.py'
spec=importlib.util.spec_from_file_location('catalog',p); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.c={'schemaVersion':1,'catalogVersion':1,'distribution':'development','entries':[{'id':'org.notchframework.hello','version':'0.1.0','protocolVersion':1,'architecture':'universal','minHostVersion':'0.1.0','size':100,'sha256':'0'*64,'downloadURL':'https://github.com/test-owner/test-repo/releases/download/v0.1.0/hello.zip','capabilities':[]}]}
    def test_development_shape(self): self.assertEqual(mod.validate(self.c),1)
    def test_duplicate(self):
        self.c['entries']*=2
        with self.assertRaises(ValueError): mod.validate(self.c)
    def test_untrusted_urls(self):
        for url in ('http://github.com/a/b/releases/download/v1/a.zip','https://evil.test/a.zip','https://github.com/a/b/releases/latest/a.zip','https://github.com@evil.test/a','https://github.com/a/b/releases/download/v1/%2e%2e'):
            with self.subTest(url=url):
                self.c['entries'][0]['downloadURL']=url
                with self.assertRaises(ValueError): mod.validate(self.c)
    def test_production_fail_closed(self):
        self.c['distribution']='production';self.c['entries'][0].update(publisherKeyID='not-trust',expectedTeamID='TESTONLY',packageSignature='not-a-signature')
        with self.assertRaisesRegex(ValueError,'disabled'): mod.validate(self.c)
    def test_limits(self):
        self.c['entries'][0]['size']=2*1024**3
        with self.assertRaises(ValueError): mod.validate(self.c)
    def test_hash_is_only_syntax(self):
        self.c['entries'][0]['sha256']='bad'
        with self.assertRaises(ValueError): mod.validate(self.c)
if __name__=='__main__': unittest.main()
