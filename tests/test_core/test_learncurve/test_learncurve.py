"""tests for vak.core.learncurve module"""
import pytest

import vak.config
import vak.constants
import vak.core.learncurve
import vak.paths


def assert_learncurve_output_matches_expected(cfg, model_name, results_path):
    assert results_path.joinpath("learning_curve.csv").exists()

    for train_set_dur in cfg.prep.train_set_durs:
        train_set_dur_root = results_path.joinpath(f"train_dur_{train_set_dur}s")
        assert train_set_dur_root.exists()

        for replicate_num in range(1, cfg.prep.num_replicates + 1):
            replicate_path = train_set_dur_root.joinpath(f"replicate_{replicate_num}")
            assert replicate_path.exists()

            assert replicate_path.joinpath("labelmap.json").exists()

            if cfg.learncurve.normalize_spectrograms:
                assert replicate_path.joinpath("StandardizeSpect").exists()

            eval_csv = sorted(replicate_path.glob(f"eval_{model_name}*csv"))
            assert len(eval_csv) == 1

            model_path = replicate_path.joinpath(model_name)
            assert model_path.exists()

            tensorboard_log = sorted(
                replicate_path.glob(f"lightning_logs/**/*events*")
            )
            assert len(tensorboard_log) == 1

            checkpoints_path = model_path.joinpath("checkpoints")
            assert checkpoints_path.exists()
            assert checkpoints_path.joinpath("checkpoint.pt").exists()
            if cfg.learncurve.val_step is not None:
                assert checkpoints_path.joinpath(
                    "max-val-acc-checkpoint.pt"
                ).exists()


def test_learncurve(specific_config, tmp_path, model, device):
    options_to_change = {"section": "LEARNCURVE", "option": "device", "value": device}

    toml_path = specific_config(
        config_type="learncurve",
        model=model,
        audio_format="cbin",
        annot_format="notmat",
        options_to_change=options_to_change,
    )

    cfg = vak.config.parse.from_toml_path(toml_path)
    model_config = vak.config.model.config_from_toml_path(toml_path, cfg.learncurve.model)
    results_path = vak.paths.generate_results_dir_name_as_path(tmp_path)
    results_path.mkdir()

    vak.core.learncurve.learning_curve(
        model_name=cfg.learncurve.model,
        model_config=model_config,
        dataset_path=cfg.learncurve.dataset_path,
        window_size=cfg.dataloader.window_size,
        batch_size=cfg.learncurve.batch_size,
        num_epochs=cfg.learncurve.num_epochs,
        num_workers=cfg.learncurve.num_workers,
        root_results_dir=None,
        results_path=results_path,
        spect_key=cfg.spect_params.spect_key,
        timebins_key=cfg.spect_params.timebins_key,
        normalize_spectrograms=cfg.learncurve.normalize_spectrograms,
        shuffle=cfg.learncurve.shuffle,
        val_step=cfg.learncurve.val_step,
        ckpt_step=cfg.learncurve.ckpt_step,
        patience=cfg.learncurve.patience,
        device=cfg.learncurve.device,
    )

    assert_learncurve_output_matches_expected(cfg, cfg.learncurve.model, results_path)


def test_learncurve_no_results_path(specific_config, tmp_path, model, device):
    root_results_dir = tmp_path.joinpath("test_learncurve_no_results_path")
    root_results_dir.mkdir()

    options_to_change = [
        {
            "section": "LEARNCURVE",
            "option": "root_results_dir",
            "value": str(root_results_dir),
        },
        {"section": "LEARNCURVE", "option": "device", "value": device},
    ]

    toml_path = specific_config(
        config_type="learncurve",
        model=model,
        audio_format="cbin",
        annot_format="notmat",
        options_to_change=options_to_change,
    )

    cfg = vak.config.parse.from_toml_path(toml_path)
    model_config = vak.config.model.config_from_toml_path(toml_path, cfg.learncurve.model)

    vak.core.learncurve.learning_curve(
        model_name=cfg.learncurve.model,
        model_config=model_config,
        dataset_path=cfg.learncurve.dataset_path,
        window_size=cfg.dataloader.window_size,
        batch_size=cfg.learncurve.batch_size,
        num_epochs=cfg.learncurve.num_epochs,
        num_workers=cfg.learncurve.num_workers,
        root_results_dir=cfg.learncurve.root_results_dir,
        results_path=None,
        spect_key=cfg.spect_params.spect_key,
        timebins_key=cfg.spect_params.timebins_key,
        normalize_spectrograms=cfg.learncurve.normalize_spectrograms,
        shuffle=cfg.learncurve.shuffle,
        val_step=cfg.learncurve.val_step,
        ckpt_step=cfg.learncurve.ckpt_step,
        patience=cfg.learncurve.patience,
        device=cfg.learncurve.device,
    )

    results_path = sorted(root_results_dir.glob(f"{vak.constants.RESULTS_DIR_PREFIX}*"))
    assert len(results_path) == 1
    results_path = results_path[0]

    assert_learncurve_output_matches_expected(cfg, cfg.learncurve.model, results_path)


@pytest.mark.parametrize(
    'dir_option_to_change',
    [
        {"section": "LEARNCURVE", "option": "root_results_dir", "value": '/obviously/does/not/exist/results/'},
        {"section": "LEARNCURVE", "option": "dataset_path", "value": '/obviously/doesnt/exist/dataset-dir'},
    ]
)
def test_learncurve_raises_not_a_directory(dir_option_to_change,
                                           specific_config,
                                           tmp_path, device):
    """Test that core.learncurve.learning_curve raises NotADirectoryError
    when the following directories do not exist:
    results_path, previous_run_path, dataset_path
    """
    options_to_change = [
        {"section": "LEARNCURVE", "option": "device", "value": device},
        dir_option_to_change
    ]
    toml_path = specific_config(
        config_type="learncurve",
        model="teenytweetynet",
        audio_format="cbin",
        annot_format="notmat",
        options_to_change=options_to_change,
    )
    cfg = vak.config.parse.from_toml_path(toml_path)
    model_config = vak.config.model.config_from_toml_path(toml_path, cfg.learncurve.model)
    # mock behavior of cli.learncurve, building `results_path` from config option `root_results_dir`
    results_path = cfg.learncurve.root_results_dir / 'results-dir-timestamp'

    with pytest.raises(NotADirectoryError):
        vak.core.learncurve.learning_curve(
            model_name=cfg.learncurve.model,
            model_config=model_config,
            dataset_path=cfg.learncurve.dataset_path,
            window_size=cfg.dataloader.window_size,
            batch_size=cfg.learncurve.batch_size,
            num_epochs=cfg.learncurve.num_epochs,
            num_workers=cfg.learncurve.num_workers,
            root_results_dir=None,
            results_path=results_path,
            spect_key=cfg.spect_params.spect_key,
            timebins_key=cfg.spect_params.timebins_key,
            normalize_spectrograms=cfg.learncurve.normalize_spectrograms,
            shuffle=cfg.learncurve.shuffle,
            val_step=cfg.learncurve.val_step,
            ckpt_step=cfg.learncurve.ckpt_step,
            patience=cfg.learncurve.patience,
            device=cfg.learncurve.device,
        )
