
Usage
=====


Installation
------------
Please be aware of the dependency of gaitalytics to Biomechanical-ToolKit (BTK). To install follow the
instructions `here <https://biomechanical-toolkit.github.io/docs/Wrapping/Python/_build_instructions.html>`_ or use
`conda-forge version <https://anaconda.org/conda-forge/btk>`_

Fast install with anaconda:

.. code-block:: bat

   pip install gaitalytics
   conda install -c conda-forge btk


Configuration
-------------
Gaitalytics can be used with any marker set, which at least includes four hip markers (left front/back, right
front/back)
and four foot markers (left heel/toe, right heel/toe) and four ankle makers (left medial/lateral, right medial lateral).

All functionalities in the libraries only take points into account which are configured in as specific yaml file.
Working example file can be found in teh example `settings file <https://github.com/cereneo-foundation/gaitalytics/blob/94bbc73072535d7f1e53ea935b6145194b137f09/settings/hbm_pig.yaml>`_



Minimal requirements would look like this:

.. code-block:: yaml
    :caption: settings.yml

    marker_set_mapping:
     left_back_hip: LASIS
     right_back_hip: RASIS
     left_front_hip: LPSIS
     right_front_hip: RPSIS

     left_lat_malleoli: LLM
     right_lat_malleoli: RLM
     left_med_malleoli: LMM
     right_med_malleoli: RMM

     right_heel: RHEE
     left_heel: LHEE
     right_meta_2: RMT2
     left_meta_2: LMT2

     com: COM
     left_cmos: cmos_left
     right_cmos: cmos_right

    model_mapping:

.. warning::
    Do not rename keys of the minimal setting

Pipeline
--------

Please take the resources in
the `example folder <https://github.com/cereneo-foundation/gaitalytics/tree/94bbc73072535d7f1e53ea935b6145194b137f09/examples>`_
for advice.
