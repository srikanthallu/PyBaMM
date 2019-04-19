#
# Equation classes for a Particle
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals
import pybamm


class Standard(pybamm.SubModel):
    """A class that generates the expression tree for Stefan-Maxwell Current in the
    electrolyte.

    Parameters
    ----------
    set_of_parameters : parameter class
        The parameters to use for this submodel

    *Extends:* :class:`pybamm.SubModel`
    """

    def __init__(self, set_of_parameters):
        super().__init__(set_of_parameters)

    def set_differential_system(self, c, j, broadcast=False):
        param = self.set_of_parameters

        if len(c.domain) != 1:
            raise NotImplementedError(
                "Only implemented when c_k is on exactly 1 subdomain"
            )

        if c.domain[0] == "negative particle":
            N = -(1 / param.C_n) * pybamm.grad(c)
            self.rhs = {c: -pybamm.div(N)}
            self.algebraic = {}
            self.initial_conditions = {c: param.c_n_init}
            self.boundary_conditions = {
                N: {"left": pybamm.Scalar(0), "right": param.C_n * j / param.a_n}
            }
            self.variables = self.get_variables(c, N, broadcast)
        elif c.domain[0] == "positive particle":
            N = -(1 / param.C_p) * pybamm.grad(c)
            self.rhs = {c: -pybamm.div(N)}
            self.algebraic = {}
            self.initial_conditions = {c: param.c_p_init}
            self.boundary_conditions = {
                N: {
                    "left": pybamm.Scalar(0),
                    "right": param.C_p * j / param.a_p / param.gamma_p,
                }
            }
            self.variables = self.get_variables(c, N, broadcast)
        else:
            raise pybamm.ModelError("Domain not valid for the particle equations")

    def get_variables(self, c, N, broadcast):
        if c.domain == ["negative particle"]:
            conc_scale = self.set_of_parameters.c_n_max
            domain = "Negative particle"
            broadcast_domain = ["negative electrode"]
        elif c.domain == ["positive particle"]:
            conc_scale = self.set_of_parameters.c_p_max
            domain = "Positive particle"
            broadcast_domain = ["positive electrode"]

        c_surf = pybamm.surf(c)
        if broadcast:
            c_surf = pybamm.Broadcast(c_surf, broadcast_domain)

        return {
            domain + " concentration": c,
            domain + " surface concentration": c_surf,
            domain + " flux": N,
            domain + " concentration [mols m-3]": conc_scale * c,
            domain + " surface concentration [mols m-3]": conc_scale * c_surf,
        }
