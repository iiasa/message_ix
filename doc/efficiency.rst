.. _efficiency_output:

Efficiency - output- vs. input defined technologies 
===================================================

There is no obvious approach whether a model should be formulated 
in a way that treats technologies as parametrized to input or output commodities/fuels - 
power plant parameters are usually understood as output-based (per unit of electricity generated), 
while refinery parameters are usually based on input fuels (per unit of input commodity processed.  
Things become even trickier when technologies have multiple inputs or outputs.
Standardizing the methodology and assumptions can become quite a challenge.
 
For the implementation of |MESSAGEix|, we opted to formulate the model in an agnostic manner, 
so that for each technology, the most "appropriate" parametrization can be applied.
As an additional benefit, we do not need to define an explicit efficiency parameter
or "main" input and output fuels.  

The recommended approach is illustrated below for multiple examples. 
The decision variables :math:`\text{CAP_NEW}`, :math:`\text{CAP}` and :math:`\text{ACT}` as well as all bounds 
are always understood to be in the same units. All cost parameters also have to be provided 
in monetary units per these units - there is no "automatic rescaling" done either within the ixmp API
or in the GAMS implementation pre- or postprocessing.

Example 1 - Power plants
~~~~~~~~~~~~~~~~~~~~~~~~

Technical specifications of power plants are commonly stated in terms of electricity generated (output). 
Therefore, the decision variables should be understood as outputs, with the parameter :math:`\text{output} = 1` 
and parameter :math:`\text{input} = \frac{1}{\text{efficiency}}`. This may seem counter-intuitive at first, but the clear 
advantage is that all technical parameters can be immediately related to values found in the literature.

Example 2 - Refineries
~~~~~~~~~~~~~~~~~~~~~~

For crude oil refineries, it is more common to scale costs and emissions 
in terms of crude oil input quantities. Hence, the parameter :math:`\text{input} = 1` 
and the output parameters (usually for multiple different oil products) 
should be set accordingly.

The decision variables and bounds are then implicitly understood as input-based.

An alternative would be to parametrize a refinery based on outputs, but 
considering that there are multiple outputs (in fixed proportions), 
the sum of output parameters over all products should be set to 1,
i.e., :math:`\sum_{c} \text{output}_{c} = 1`. The input of crude oil should then 
include the losses during the refining process,  :math:`\text{input} > 1`.
 
Example 3 - Combined power- and heat plants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a third option, technical specifications of combined heat- and power plants
are usually also given with regard to electricity generated under the 
assumption that the electricity generated is maximized. Then, as in example 1,
the capacity and activity variables should be understood as electricity generated.

Assuming that such a plant usually has (at least) two modes of operation, these 
modes could be parametrized as follows:

:math:`\text{input} = \frac{1}{\text{efficiency}}`

:math:`\text{output}_{\text{M1},\text{electricity}} = 1` and :math:`\text{output}_{\text{M1},\text{heat}} = 0.2`

:math:`\text{output}_{\text{M2},\text{electricity}} = 0.5` and :math:`\text{output}_{\text{M2}, \text{heat}} = 3`.

Note that the activity level in mode 'M2' has an odd interpretation - the amount 
of electricity generated if electricity generation were maximized. The sum of outputs 
is greater than 1 in either mode. However, we believe that this approach at least
has the benefit of a parametrization that can be directly related to technical reports.    



 

  