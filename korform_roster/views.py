from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from extra_views import ModelFormSetView
from korform_planning.models import Group
from .models import Member, Contact, RSVP
from .forms import MemberForm, ContactForm, RSVPForm, RSVPFormSet, RSVPFormSetHelper

class CustomFormMixin(object):
    form_spec_path = ''
    
    def get_form_spec(self):
        assert len(self.form_spec_path) > 0
        
        val = self
        for part in self.form_spec_path.split('.'):
            val = getattr(val, part)
        return val
    
    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.get_form_class()
        return form_class(self.get_form_spec(), **self.get_form_kwargs())



class MemberView(DetailView):
    model = Member
    context_object_name = 'member'

class MemberPickGroupView(TemplateView):
    template_name = 'korform_roster/member_group.html'
    
    def get_context_data(self, **kwargs):
        context = super(MemberPickGroupView, self).get_context_data(**kwargs)
        context['groups'] = self.request.site.config.current_term.groups.all()
        return context

class MemberCreateView(CustomFormMixin, CreateView):
    model = Member
    context_object_name = 'member'
    form_class = MemberForm
    form_spec_path = 'request.site.config.current_term.form'
    
    def get_group(self):
        return get_object_or_404(Group, slug=self.kwargs['group'])
    
    def get_context_data(self, **kwargs):
        context = super(MemberCreateView, self).get_context_data(**kwargs)
        context['group'] = self.get_group()
        return context
    
    def form_valid(self, form):
        form.instance.site = self.request.site
        form.instance.group = self.get_group()
        form.instance.profile = self.request.user.profile
        return super(MemberCreateView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('member_rsvp', kwargs={'pk': self.object.pk})

class MemberUpdateView(CustomFormMixin, UpdateView):
    model = Member
    context_object_name = 'member'
    form_class = MemberForm
    form_spec_path = 'request.site.config.current_term.form'

class MemberRSVPView(ModelFormSetView):
    template_name = 'korform_roster/member_rsvp.html'
    model = RSVP
    form_class = RSVPForm
    formset_class = RSVPFormSet
    fields = RSVPForm.Meta.fields
    
    def get_member(self):
        return get_object_or_404(Member, pk=self.kwargs['pk'])
    
    def get_events(self):
        return self.get_member().get_events_missing_rsvp()
    
    def get_factory_kwargs(self):
        kwargs = super(MemberRSVPView, self).get_factory_kwargs()
        events = self.get_events()
        kwargs['extra'] = 0
        kwargs['max_num'] = len(events)
        kwargs['min_num'] = len(events)
        return kwargs
    
    def get_formset_kwargs(self):
        kwargs = super(MemberRSVPView, self).get_formset_kwargs()
        kwargs['member'] = self.get_member()
        kwargs['events'] = self.get_events()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(MemberRSVPView, self).get_context_data(**kwargs)
        context['member'] = self.get_member()
        context['events'] = self.get_events()
        context['helper'] = RSVPFormSetHelper()
        return context
    
    def get_queryset(self):
        return RSVP.objects.none()
    
    def get_success_url(self):
        return self.get_member().get_absolute_url()

class ContactView(DetailView):
    model = Contact
    context_object_name = 'contact'

class ContactCreateView(CustomFormMixin, CreateView):
    model = Contact
    context_object_name = 'contact'
    form_class = ContactForm
    form_spec_path = 'request.site.config.contact_form'
    
    def form_valid(self, form):
        form.instance.site = self.request.site
        form.instance.profile = self.request.user.profile
        return super(ContactCreateView, self).form_valid(form)

class ContactUpdateView(CustomFormMixin, UpdateView):
    model = Contact
    context_object_name = 'contact'
    form_class = ContactForm
    form_spec_path = 'request.site.config.contact_form'
