from firesynth import FireSynthS2

def test_generation():
    gen = FireSynthS2()
    df = gen.generate(1000)
    assert len(df) == 2000
    assert "NDVI" in df.columns
